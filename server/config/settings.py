"""
(C) Copyright 2017 SLU Global Bioinformatics Centre, SLU
(http://sgbc.slu.se) and the eBioKit Project (http://ebiokit.eu).

This file is part of The eBioKit portal 2017. All rights reserved.
The eBioKit portal is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with eBioKit portal.  If not, see <http://www.gnu.org/licenses/>.

Contributors:
    Dr. Erik Bongcam-Rudloff
    Dr. Rafael Hernandez de Diego (main developer)
    and others.

 More info http://ebiokit.eu/
 Technical contact ebiokit@gmail.com
"""

import os
import random
import string

# -----------------------------------------------------------------------------------------------------------------------------------------
# CUSTOM SETTINGS FOR THE APPLICATION
# -----------------------------------------------------------------------------------------------------------------------------------------
APP_VERSION = 18.08

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "True") == "True"
if DEBUG:
    print("ATTENTION: DEBUG MODE IS ON")
# -----------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "".join(random.choice(string.printable) for i in range(40)))

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Django Packages
    'rest_framework',
    'applications'
]


MIDDLEWARE_CLASSES = [
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser'
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer'
    ]
}

ROOT_URLCONF = 'urls'

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_URL = '/static/'

if DEBUG:
    FRONTEND_ROOT = (os.path.join(BASE_DIR, '../client'))
    STATICFILES_DIRS = [FRONTEND_ROOT]
    TEMPLATE_DIRS = [FRONTEND_ROOT]
else:
    STATIC_ROOT=(os.path.join(BASE_DIR, 'static'))
    STATICFILES_DIRS = [os.path.join(BASE_DIR, '../client/dist')]
    TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'static')]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':  TEMPLATE_DIRS,
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE_NAME', 'ebiokit_db'),
        'USER': os.environ.get('MYSQL_ROOT_USER', 'root'),
        'PASSWORD': os.environ.get('MYSQL_ROOT_PASSWORD', '123123'),
        'HOST': os.environ.get('MYSQL_HOST', '0.0.0.0')
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_L10N = True
USE_TZ = True
