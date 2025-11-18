from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
import os
from pathlib import Path


# # Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# # Quick-start development settings - unsuitable for production
# # See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# # SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.getenv("SECRET_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# ✅ Force www redirect
# SECURE_SSL_REDIRECT = True
# PREPEND_WWW = True



# ALLOWED_HOSTS = ['homedeninterior.com', 'www.homedeninterior.com', 'srv888437.hstgr.cloud', '127.0.0.1', 'localhost']
ALLOWED_HOSTS = [
    "homedeninterior.com",
    "www.homedeninterior.com",
    "srv888437.hstgr.cloud",
    "127.0.0.1",
    "localhost",
]



# Application definition

INSTALLED_APPS = [
    # "admin_interface",
    # "colorfield",#FOR ADMIN INTERFACE
    'jazzmin',

    'django.contrib.sitemaps',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'elite_interior',
    
    'widget_tweaks',
]


JAZZMIN_SETTINGS = {
    "site_title": "HOME DEN Admin",
    "site_header": "HOME DEN Admin",
    "site_brand": "HOME DEN",
    "welcome_sign": "Welcome to HOME DEN Admin",
    "copyright": "HOME DEN",

    # 👇 Add your logo here
    "site_logo": "images/home_den.png",  # path inside STATICFILES_DIRS
    "site_logo_classes": "img-fluid",  # optional (can use img-square, img-fluid, etc.)
    "login_logo": "images/home_den.png",    # logo for login page (optional)
    "login_logo_dark": None,            # alternative for dark mode (optional)

    "topmenu_links": [
        {"name": "Home",  "url": "/", "permissions": ["auth.view_user"]},
        {"model": "your_app.homeslider"},
    ],
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": True,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_small_text": True,
    "brand_colour": "navbar-dark",
    "accent": "accent-info",
    "navbar": "navbar-dark navbar-primary",
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar_nav_small_text": True,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
}


JAZZMIN_SETTINGS["icons"] = {
        # Built-in auth models
        "auth.User": "fas fa-user",        # Users
        "auth.Group": "fas fa-users-cog",  # Groups

        "elite_interior.HomeSlider": "fas fa-image",
        "elite_interior.PackageOffers": "fas fa-tags",
        "elite_interior.WhatWeDo_Grid": "fas fa-th-large",
        "elite_interior.Testimonial": "fas fa-comment-dots",
        "elite_interior.BlogCategory": "fas fa-folder-open",
        "elite_interior.AboutVideo": "fas fa-video",
        "elite_interior.YouTubeVideoProjects": "fab fa-youtube",
        "elite_interior.BudgetItem": "fas fa-file-invoice-dollar",
        "elite_interior.Category": "fas fa-list",
        "elite_interior.SubCategory": "fas fa-list-ul",
        "elite_interior.OtpVerification": "fas fa-key",
        "elite_interior.Project": "fas fa-project-diagram",
        "elite_interior.Blog": "fas fa-blog",
        "elite_interior.YouTubeVideo": "fab fa-youtube",
        "elite_interior.ProjectGallery": "fas fa-images",
        "elite_interior.Product": "fas fa-box",
        "elite_interior.ProductCategory": "fas fa-tags",
        "elite_interior.Brand": "fas fa-copyright",
        "elite_interior.Unit": "fas fa-ruler-combined",
        "elite_interior.TeamMember": "fas fa-users",
        "elite_interior.Ad": "fas fa-ad",
        "elite_interior.Accessory": "fas fa-cogs",
}



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'interior.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "elite_interior" / "templates" / "elite_interior"],

        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'interior.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'home_den',
        'USER': 'root',
        'PASSWORD': os.getenv("DB_PASSWORD"),

        'HOST': 'localhost',
        'PORT': '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage" 
ROOT_URLCONF = 'interior.urls'




# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# STATIC_URL = '/static/'
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'interior', 'static',)]
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'interior', 'static'),  # 👈 this tells Django where to look
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# email
EMAIL_FILE_PATH = 'emails'  # Emails will be saved in this folder
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# for serve the mail

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.gmail.com'  # Use your SMTP provider
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'homedeninterior@gmail.com'
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD") # Use environment variables instead for security
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "homedeninterior@gmail.com")


# for whatsapp message





"""
Django settings for interior project.

Generated by 'django-admin startproject' using Django 5.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""






