import os 
from pathlib import Path
from whitenoise import WhiteNoise

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-mqnu-8oeu7f$h)3ch6wh6ugv*_bjzo#qx1epp&#s6csu0g7%rl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'classnest_Base',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware'
]

CSRF_TRUSTED_ORIGINS = [
    'https://classnest.up.railway.app',
    'https://nonest.up.railway.app/'
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

CORS_ALLOWED_ORIGINS = [
    'https://classnest.up.railway.app',
    'https://nonest.up.railway.app/'
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
ROOT_URLCONF = 'classnest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'classnest_Base', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'classnest.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'railway',  # Use the name provided in the Railway dashboard
        'USER': 'postgres',  # Replace with the correct username
        'PASSWORD': 'aJhVCnMbqJQuXDFFKBSJSktseDmeJGdK',  # Replace with the actual password
        'HOST': 'autorack.proxy.rlwy.net',  # Use the public host
        'PORT': '29812',  # Use the provided public port
        'OPTIONS': {
            'sslmode': 'require',  # Ensure secure connection
        },
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True




STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'classnest_Base', 'static')
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')



# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'dashboard'  # Redirect users to the dashboard after login
LOGOUT_REDIRECT_URL = 'login'  # Redirect users to the login page after logout


# Set session to persist indefinitely
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use database-backed sessions
SESSION_COOKIE_AGE = 31536000  # 1 year in seconds (Adjust as needed)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Prevent session from expiring when the browser closes
