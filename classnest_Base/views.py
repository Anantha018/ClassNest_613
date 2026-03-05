# classnest_Base/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.models import User
from classnest_Base.models import Profile
from django.db.models import Q
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Create groups if they don’t already exist
def create_user_groups():
    Group.objects.get_or_create(name='Student')
    Group.objects.get_or_create(name='Instructor')


create_user_groups()

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_type = form.cleaned_data.get('user_type')
            if user_type == 'student':
                group = Group.objects.get(name='Student')
            elif user_type == 'instructor':
                group = Group.objects.get(name='Instructor')
            user.groups.add(group)

            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'classnest_Base/register.html', {'form': form})


@method_decorator(csrf_exempt, name='dispatch')
class CustomLoginView(LoginView):
    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if remember_me:
            self.request.session.set_expiry(31536000)
        else:
            self.request.session.set_expiry(0)
        return super().form_valid(form)
    
@login_required
def dashboard_view(request):
    # Debugging: Print user and their groups
    print(f"User: {request.user}")
    print(f"User groups: {request.user.groups.all()}")

    # Check if the user is in the 'Instructor' group
    is_instructor = request.user.groups.filter(name='Instructor').exists()
    
    # Debugging: Print the result of the check
    print(f"Is instructor: {is_instructor}")
    
    return render(request, 'classnest_Base/dashboard.html', {'is_instructor': is_instructor})


@login_required
def create_course_view(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('courses')  # Redirect to the courses or another page after creating the course
        else:
            print("Form errors:", form.errors)
    else:
        form = CourseForm()  # Initialize an empty form for GET requests

    return render(request, 'classnest_Base/create_course.html', {'form': form})

@login_required
def courses_view(request):
    is_instructor = request.user.groups.filter(name='Instructor').exists()  # Use 'Instructor' instead of 'Instructors'
    courses = Course.objects.all()
    return render(request, 'classnest_Base/courses.html', {'courses': courses, 'is_instructor': is_instructor})

@login_required
def search_courses_view(request):
    query = request.GET.get('q')  # Get the search query from the URL
    if query:
        courses = Course.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )  # Search by course title or description
    else:
        courses = Course.objects.all()

    return render(request, 'classnest_Base/courses.html', {'courses': courses})

@login_required
def course_detail_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_instructor = request.user.groups.filter(name='Instructor').exists()
    modules = Module.objects.filter(course=course)

    # Handle enrollment for students
    if request.method == "POST" and 'enroll' in request.POST:
        if not is_instructor:
            course.students.add(request.user)
            messages.success(request, "You have successfully enrolled in the course.")
            return redirect('dashboard')

    return render(request, 'classnest_Base/course_detail.html', {
        'course': course,
        'is_instructor': is_instructor,
        'modules': modules
    })


@login_required
def delete_course_view(request, course_id):
    # Get the course object or return a 404 error if not found
    course = get_object_or_404(Course, id=course_id)
    
    # Check if the user is the instructor who created the course or an admin
    if request.user == course.instructor or request.user.is_superuser:
        course.delete()  # Delete the course
        # Redirect to the courses page with a success message (optional)
        return redirect('courses')
    else:
        # If the user is not authorized, return a forbidden response
        return HttpResponseForbidden("You are not allowed to delete this course.")

@login_required
def add_module_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.user != course.instructor:
        return HttpResponseForbidden("You are not allowed to add modules to this course.")
    
    return render(request, 'classnest_Base/add_module.html', {'course': course})

@login_required
def save_module_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user != course.instructor:
        return HttpResponseForbidden("You are not allowed to add modules to this course.")

    if request.method == "POST":
        # Save the module
        module_title = request.POST.get('module_title')
        module = Module.objects.create(title=module_title, course=course)

        # Save recordings as URLs
        recording_urls = request.POST.getlist('recordings')
        recording_titles = request.POST.getlist('recording_title')  # Get the titles
        for url, title in zip(recording_urls, recording_titles):
            if url.strip():  # Check if the URL is not empty
                Recording.objects.create(module=module, title=title, url=url)

        # Save assignment files
        assignments = request.FILES.getlist('assignments')
        assignment_titles = request.POST.getlist('assignment_title')  # Get the titles
        for file, title in zip(assignments, assignment_titles):
            Assignment.objects.create(module=module, title=title, file=file)

        # Save material files
        materials = request.FILES.getlist('materials')
        material_titles = request.POST.getlist('material_title')  # Get the titles
        for file, title in zip(materials, material_titles):
            Material.objects.create(module=module, title=title, file=file)

        return redirect('course-detail', course_id=course.id)

    return render(request, 'classnest_Base/add_module.html', {'course': course})

@login_required
def module_detail_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    course = module.course  # Ensure you have the course related to the module

    # Retrieve related content using the related manager
    recordings = module.recording_set.all()
    assignments = module.assignment_set.all()
    materials = module.material_set.all()

    # Pass the course object to the template
    return render(request, 'classnest_Base/module_detail.html', {
        'module': module,
        'course': course,
        'recordings': recordings,
        'assignments': assignments,
        'materials': materials,
    })


@login_required
# View to add a recording
def add_recording_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.user != module.course.instructor:
        return HttpResponseForbidden("You are not allowed to add recordings to this module.")

    if request.method == "POST":
        title = request.POST.get('recording_title')
        url = request.POST.get('recording_url')
        if title and url:
            Recording.objects.create(module=module, title=title, url=url)
        return redirect('module-detail', module.id)

@login_required
# View to add an assignment
def add_assignment_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.user != module.course.instructor:
        return HttpResponseForbidden("You are not allowed to add assignments to this module.")

    if request.method == "POST" and request.FILES.get('assignment_file'):
        title = request.POST.get('assignment_title')
        file = request.FILES.get('assignment_file')
        if title and file:
            Assignment.objects.create(module=module, title=title, file=file)
        return redirect('module-detail', module.id)

@login_required
# View to add a material
def add_material_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.user != module.course.instructor:
        return HttpResponseForbidden("You are not allowed to add materials to this module.")

    if request.method == "POST" and request.FILES.get('material_file'):
        title = request.POST.get('material_title')
        file = request.FILES.get('material_file')
        if title and file:
            Material.objects.create(module=module, title=title, file=file)
        return redirect('module-detail', module.id)
 
@login_required   
# View to delete a recording
def delete_recording_view(request, recording_id):
    recording = get_object_or_404(Recording, id=recording_id)
    if request.user != recording.module.course.instructor:
        return HttpResponseForbidden("You are not allowed to delete this recording.")

    if request.method == "POST":
        recording.delete()
        return redirect('module-detail', recording.module.id)

@login_required
# View to delete an assignment
def delete_assignment_view(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.user != assignment.module.course.instructor:
        return HttpResponseForbidden("You are not allowed to delete this assignment.")

    if request.method == "POST":
        assignment.delete()
        return redirect('module-detail', assignment.module.id)

@login_required
# View to delete a material
def delete_material_view(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    if request.user != material.module.course.instructor:
        return HttpResponseForbidden("You are not allowed to delete this material.")

    if request.method == "POST":
        material.delete()
        return redirect('module-detail', material.module.id)

@login_required
def delete_module_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    # Check if the user is the instructor of the module
    if request.user == module.course.instructor:
        module.delete()  # Delete the module and its related content
        return redirect('course-detail', course_id=module.course.id)  # Redirect to the course detail page
    else:
        return HttpResponseForbidden("You are not allowed to delete this module.")
    
@login_required
def dashboard_view(request):
    is_instructor = request.user.groups.filter(name='Instructor').exists()
    if is_instructor:
        # Fetch courses created by the instructor
        instructed_courses = Course.objects.filter(instructor=request.user)
        return render(request, 'classnest_Base/dashboard.html', {
            'is_instructor': is_instructor,
            'instructed_courses': instructed_courses
        })
    else:
        # Fetch courses the student is enrolled in
        enrolled_courses = request.user.enrolled_courses.all()
        return render(request, 'classnest_Base/dashboard.html', {
            'is_instructor': is_instructor,
            'enrolled_courses': enrolled_courses
        })

@login_required
def profile_view(request):
    # Ensure the profile exists for the user
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == "POST":
        new_email = request.POST.get("email")
        github_link = request.POST.get("github")
        linkedin_link = request.POST.get("linkedin")

        if new_email:
            if new_email != request.user.email:
                if User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
                    messages.error(request, "This email address is already in use.")
                else:
                    request.user.email = new_email
                    request.user.save()
                    messages.success(request, "Your email has been updated successfully!")
            else:
                messages.info(request, "This is already your email.")
        
        # Update GitHub and LinkedIn links
        profile.github_link = github_link
        profile.linkedin_link = linkedin_link
        profile.save()
        messages.success(request, "Social links updated successfully!")

    return render(request, 'classnest_Base/profile.html', {
        'current_email': request.user.email,
        'github_link': profile.github_link,
        'linkedin_link': profile.linkedin_link,
    })

@login_required
def discussions_view(request):
    user = request.user
    selected_course_id = request.GET.get('course_id', None)

    # Fetch courses the user is enrolled in or instructing
    courses = Course.objects.filter(models.Q(students=user) | models.Q(instructor=user)).distinct()

    # Filter discussions by the selected course or show all discussions
    if selected_course_id:
        discussions = Discussion.objects.filter(course_id=selected_course_id)
    else:
        discussions = Discussion.objects.filter(course__in=courses)

    # Check if the user is an instructor
    is_instructor = Course.objects.filter(instructor=user).exists()

    context = {
        'courses': courses,
        'discussions': discussions,
        'selected_course_id': selected_course_id,
        'is_instructor': is_instructor,
    }
    return render(request, 'classnest_Base/discussions.html', context)



@login_required
def user_discussions(request):
    user = request.user

    # Get courses the user is enrolled in or instructing
    enrolled_courses = Course.objects.filter(students=user)
    instructed_courses = Course.objects.filter(instructor=user)

    # Get discussions for these courses
    discussions = Discussion.objects.filter(course__in=enrolled_courses | instructed_courses).distinct()

    context = {
        'discussions': discussions,
    }
    return render(request, 'classnest_Base/discussions.html', context)

@login_required
def discussion_detail(request, discussion_id):
    discussion = get_object_or_404(Discussion, id=discussion_id)

    # Ensure the user has access to this discussion
    if not (request.user == discussion.instructor or request.user in discussion.course.students.all()):
        return HttpResponseForbidden("You do not have permission to view this discussion.")

    return render(request, 'classnest_Base/discussion_detail.html', {'discussion': discussion})


@login_required
def discussion_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Check if the user is enrolled or is the instructor
    if request.user != course.instructor and request.user not in course.students.all():
        return HttpResponseForbidden("You are not authorized to view these discussions.")

    # Fetch all discussions for the course
    discussions = Discussion.objects.filter(course=course)

    return render(request, 'classnest_Base/discussion_list.html', {
        'course': course,
        'discussions': discussions,
    })

@login_required
def discussion_list_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if the user is the instructor or an enrolled student
    if request.user != course.instructor and request.user not in course.students.all():
        return redirect('dashboard')  # Redirect unauthorized users
    
    discussions = course.discussions.all()
    return render(request, 'classnest_Base/discussions.html', {'course': course, 'discussions': discussions})

@login_required
def create_discussion(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user != course.instructor:
        return HttpResponseForbidden("You are not authorized to create a discussion for this course.")

    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.course = course  # Assign the course directly
            discussion.instructor = request.user  # Set the instructor
            discussion.save()
            return redirect(f'/discussions/?course_id={course_id}')
    else:
        form = DiscussionForm()

    return render(request, 'classnest_Base/create_discussion.html', {'form': form, 'course': course})


@login_required
def delete_discussion(request, discussion_id):
    discussion = get_object_or_404(Discussion, id=discussion_id)

    if request.user != discussion.instructor:
        return HttpResponseForbidden("You are not authorized to delete this discussion.")

    course_id = discussion.course.id
    discussion.delete()

    return redirect(f'/discussions/?course_id={course_id}')


@login_required
def inbox_view(request):
    # Debugging: Print user and their groups
    print(f"User: {request.user}")
    print(f"User groups: {request.user.groups.all()}")
    # Fetch all discussions, ordered by creation date
    inbox_messages = Inbox.objects.filter(instructor=request.user).order_by('-created_at')

    # Check if the user is an instructor
    is_instructor = request.user.groups.filter(name='Instructors').exists()

    # Render the inbox page
    return render(request, 'classnest_Base/inbox.html', {
        'inbox_messages': inbox_messages,
        'is_instructor': is_instructor,
    })

@login_required
def create_inbox_view(request):
    # Check if the user is in the 'Instructor' group
    is_instructor = request.user.groups.filter(name='Instructor').exists()
    
    if request.method == "POST":
        form = InboxForm(request.POST)
        if form.is_valid():
            inbox = form.save(commit=False)
            inbox.instructor = request.user
            inbox.save()
            return redirect('inbox')  # Redirect to the dashboard or another page after creating the course
        else:
            print("Form errors:", form.errors)
    else:
        form = CourseForm()  # Initialize an empty form for GET requests

    return render(request, 'classnest_Base/create_inbox.html', {'form': form, 'is_instructor': is_instructor})

@login_required
def inbox_detail_view(request, inbox_id):
    inbox = get_object_or_404(Inbox, id=inbox_id)
    is_instructor = request.user == inbox.instructor
    return render(request, 'classnest_Base/inbox_detail.html', {
        'message': inbox,
        'is_instructor': is_instructor
    })
    
@login_required
def delete_inbox_view(request, inbox_id):
    # Get the course object or return a 404 error if not found
    inbox = get_object_or_404(Inbox, id=inbox_id)
    
    # Check if the user is the instructor who created the course or an admin
    if request.user == inbox.instructor or request.user.is_superuser:
        inbox.delete()  # Delete the course
        # Redirect to the courses page with a success message (optional)
        return redirect('inbox')
    else:
        # If the user is not authorized, return a forbidden response
        return HttpResponseForbidden("You are not allowed to delete this Conversation.")
    

@login_required
def edit_course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = CourseEditForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('course-detail', course_id=course.id)
    else:
        form = CourseEditForm(instance=course)
    return render(request, 'classnest_Base/edit_course.html', {'form': form, 'course': course})


@login_required
def send_message_view(request):
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']
            Message.objects.create(sender=request.user, receiver=recipient, subject=subject, body=body)
            messages.success(request, "Message sent successfully!")
            return redirect('inbox')  # Redirect to inbox after sending
    else:
        form = MessageForm()

    return render(request, 'classnest_Base/send_message.html', {'form': form})


@login_required
def inbox_view(request):
    received_messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'classnest_Base/inbox.html', {'messages': received_messages})


@login_required
def message_detail_view(request, message_id):
    message = Message.objects.get(id=message_id, receiver=request.user)
    message.is_read = True  # Mark the message as read
    message.save()
    return render(request, 'classnest_Base/message_detail.html', {'message': message})

@login_required
def instructor_detail_view(request, instructor_id):
    instructor = get_object_or_404(User, id=instructor_id)
    context = {
        'instructor': instructor,
    }
    return render(request, 'classnest_Base/instructor_detail.html', context)

@login_required
def enrolled_students_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = course.students.all()  # Fetch all enrolled students
    context = {
        'course': course,
        'students': students,
    }
    return render(request, 'classnest_Base/enrolled_students.html', context)

@login_required
def user_profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    context = {
        'user_profile': user,
    }
    return render(request, 'classnest_Base/user_profile.html', context)