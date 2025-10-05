from pathlib import Path

# Répertoire racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Clé secrète (à externaliser en prod via variable d'environnement)
SECRET_KEY = 'django-insecure-!b6a-ncnqv3=!phpk@ld8wopu23-)oxv8#xu31nz-k$)rd&tt='

# Mode développement (DEBUG=False en production)
DEBUG = True

# Hôtes autorisés (à compléter en production)
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Apps Django de base
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Bibliothèques tierces
    "corsheaders",      # Gestion du CORS pour le front
    "rest_framework",   # Django REST Framework (API)
    "drf_spectacular",  # Schéma OpenAPI

    # Applications du projet
    "users",            # Modèle utilisateur personnalisé (AUTH_USER_MODEL)
    "projects_app",     # Projets, contributeurs, issues, commentaires
]

# Modèle utilisateur personnalisé
AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Le CORS doit être déclaré en premier
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Fichier de configuration des URL
ROOT_URLCONF = "softdesk.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # Dossiers de templates supplémentaires si besoin
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Point d'entrée WSGI
WSGI_APPLICATION = "softdesk.wsgi.application"

# Base de données (SQLite pour le développement)
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
}

# Validations de mot de passe (par défaut)
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalisation
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Fichiers statiques
STATIC_URL = "static/"

# Clé primaire par défaut pour les nouveaux modèles
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuration DRF (auth, permissions, pagination, schéma)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",  # Authentification JWT
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",  # API privée par défaut
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",  # Pagination simple
    "PAGE_SIZE": 20,  # Taille de page par défaut
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",  # Schéma OpenAPI
}

# drf-spectacular : métadonnées du schéma
SPECTACULAR_SETTINGS = {
    "TITLE": "SoftDesk Support API",
    "VERSION": "1.0.0",
}

# Option production : limitation de débit (anti brute-force / DoS)
# Aucun effet en développement (DEBUG=True)
if not DEBUG:
    REST_FRAMEWORK.update({
        "DEFAULT_THROTTLE_CLASSES": (
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
        ),
        "DEFAULT_THROTTLE_RATES": {
            "anon": "100/hour",   # Limite pour les utilisateurs anonymes
            "user": "1000/hour",  # Limite pour les utilisateurs authentifiés
        },
    })
