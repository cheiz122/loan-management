import os
from pathlib import Path
from django.urls import reverse_lazy # type: ignore

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-3fr3j323rjgezg9)kvx$@1mps_-d%2_wu48ffi$m2zr-qbwu42'

DEBUG = True

CSRF_TRUSTED_ORIGINS = [ 
   
   'https://reasonably-master-goat.ngrok-free.app',
]
ALLOWED_HOSTS = [
    '105.163.158.144' # Your public IP address
    '192.168.0.104',  # Your local IP address
    'localhost',
    '127.0.0.1',
    'reasonably-master-goat.ngrok-free.app',
    'loan-management-1-d6h3.onrender.com'
    
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'chegep122@gmail.com'
EMAIL_HOST_PASSWORD = 'gmho xgen sgov vzui'
DEFAULT_FROM_EMAIL = 'chegep122@gmail.com'


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'customer_management_app',  # Your custom app
    'django_plotly_dash',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'customer_management_app.middleware.AdminAccessMiddleware', 
    'django.middleware.csrf.CsrfViewMiddleware', # Custom middleware for admin access control
    'django_plotly_dash.middleware.BaseMiddleware',
    'django_plotly_dash.middleware.ExternalRedirectionMiddleware',
]

ROOT_URLCONF = 'customer_management.urls'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',  # Ensure this line is present
            ],
        },
    },
]


WSGI_APPLICATION = 'customer_management.wsgi.application'
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dimalink_ventures',   # Replace with your database name
        'USER': 'root',                # Replace with your MySQL username
        'PASSWORD': 'chegep122',       # Replace with your MySQL password
        'HOST': 'localhost',           # MySQL host (use '127.0.0.1' if 'localhost' doesn't work)
        'PORT': '3306',                # MySQL port (default is 3306)
    }
}
'''

import os
import environ

env = environ.Env()
environ.Env.read_env()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT', default='5432'),
    }
}



LOGIN_URL = '/login/'  # URL for login page
LOGOUT_URL = '/logout/'  # URL for logout page
LOGIN_REDIRECT_URL = '/dashboard/'  # Redirect after successful login
LOGOUT_REDIRECT_URL = '/login/'  # Redirect after logout
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_URL = '/static/'  

STATICFILES_DIRS = [
    BASE_DIR / "customer_management_app" / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
