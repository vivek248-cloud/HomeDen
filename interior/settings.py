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

DEBUG = False  # Set to False for production

# ✅ Force www redirect
# SECURE_SSL_REDIRECT = True
# PREPEND_WWW = True



# ALLOWED_HOSTS = ['homedeninterior.com', 'www.homedeninterior.com', 'srv888437.hstgr.cloud', '127.0.0.1', 'localhost']
ALLOWED_HOSTS = ["homedeninterior.com","www.homedeninterior.com","srv888437.hstgr.cloud","127.0.0.1","localhost",]



# SECURE_BROWSER_XSS_FILTER = True

# SECURE_CONTENT_TYPE_NOSNIFF = True

# SESSION_COOKIE_SECURE = True

# CSRF_COOKIE_SECURE = True

# SECURE_SSL_REDIRECT = True

# SECURE_HSTS_SECONDS = 31536000

# SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# SECURE_HSTS_PRELOAD = True






#CACHE CONTROL
WHITENOISE_MAX_AGE = 31536000




# Application definition

INSTALLED_APPS = [
    
    "admin_interface",
    "colorfield",

    'compressor',

    'django.contrib.sitemaps',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'elite_interior',
    # 'elite_interior.apps.EliteInteriorConfig',  # <-- Missing comma fixed

    'widget_tweaks',
    'django.contrib.humanize',   # <-- Add this
    
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

]




ROOT_URLCONF = 'interior.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / "templates",
            BASE_DIR / "elite_interior" / "templates" / "elite_interior"
        ],

        'APP_DIRS': False,

        'OPTIONS': {

            'loaders': [

                (
                    'django.template.loaders.cached.Loader',
                    [
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ],
                ),

            ],

            'context_processors': [

                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',

                'elite_interior.context_processors.site_settings',

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
        'PASSWORD': 'Admin123',

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


STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

ROOT_URLCONF = 'interior.urls'


# 👇 ADD THIS LINE TO ALLOW IFRAMES ON THE SAME DOMAIN (which is necessary for YouTube embeds)
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True






STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'interior', 'static'),  # 👈 this tells Django where to look
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


STATICFILES_FINDERS = [

    'django.contrib.staticfiles.finders.FileSystemFinder',

    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

    'compressor.finders.CompressorFinder',

]



#compressor settings





COMPRESS_ENABLED = True

COMPRESS_OFFLINE = True

COMPRESS_ROOT = STATIC_ROOT

COMPRESS_URL = STATIC_URL







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





LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/quotation/"
LOGOUT_REDIRECT_URL = "/accounts/login/"



# google place ID for homeden interior


place_id = "ChIJqz7niLI4FqcRUwGcqCXHMT4"

GOOGLE_API_KEY = "AIzaSyCSSg4JvbsfUPX51r4FRz4hvqf88vyVcV4"

GOOGLE_PLACE_ID = "ChIJqz7niLI4FqcRUwGcqCXHMT4"