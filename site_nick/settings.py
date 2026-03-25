import os
from pathlib import Path
from decouple import config

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool, default=False)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost',
    cast=lambda v: [s.strip() for s in v.split(',')]
)
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='',
    cast=lambda v: [s.strip() for s in v.split(',')] if v else []
)

# Application definition

INSTALLED_APPS = [
    'adminsortable2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
    'cloudinary_storage',
    'app',
    'produtos',
    'carrinho',
    'marketing',
    'pedidos',
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

ROOT_URLCONF = 'site_nick.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'carrinho.context_processors.carrinho_context',
                'produtos.context_processors.categorias_menu',
                'pedidos.context_processors.social_links',
            ],
        },
    },
]

WSGI_APPLICATION = 'site_nick.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'pt-BR'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "app" / "static",
]


MEDIA_URL = '/media/'
MEDIA_ROOT = config('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))
STATIC_ROOT = config('STATIC_ROOT', default=os.path.join(BASE_DIR, 'staticfiles'))


LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'


MERCADO_PAGO_ACCESS_TOKEN = config('MERCADO_PAGO_ACCESS_TOKEN')
MERCADO_PAGO_PUBLIC_KEY = config('MERCADO_PAGO_PUBLIC_KEY')
SITE_URL = config('SITE_URL', default='http://localhost:8000')

MELHOR_ENVIO_TOKEN = config('MELHOR_ENVIO_TOKEN', default='')
CEP_LOJA = config('CEP_LOJA', default='')


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = 'Mimos da Nick Personalizados <mimosdanickpersonalizados@gmail.com>'


SOCIAL_LINKS = {
    "facebook": "https://www.facebook.com/people/Mimos-da-Nick-Personalizados/61557583673989/?rdid=czuOSwCRiSq5nO7C&share_url=https%3A%2F%2Fwww.facebook.com%2Fshare%2F14YgUSQvCeY%2F",
    "instagram": "https://instagram.com/mimosdanickpersonalizados",
    "whatsapp": "https://wa.me/5521992536502?text=Olá%2C%20vim%20pelo%20site%20e%20gostaria%20de%20mais%20informações",
    "email": "mimosdanickpersonalizados@gmail.com",
}


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = 'DENY'

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 3600  # 1 hora
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


import cloudinary
import cloudinary.uploader
import cloudinary.api

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'