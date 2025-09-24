# SoftDesk Support API (Django REST Framework) — Setup SQLite

API RESTful pour gérer projets, tickets (issues) et commentaires, avec authentification **JWT**, **permissions** par rôle, conformité **RGPD**, et **pagination** (green code). Cette étape 1 utilise **SQLite** (par défaut) pour un démarrage rapide.

---

## Prérequis
- Python 3.10+ (recommandé 3.11+)
- Git et un compte GitHub

> Optionnel : vous pouvez utiliser Poetry. Ici, on montre une installation **sans** Poetry pour aller au plus simple avec SQLite.

---

## Installation locale (sans Poetry, SQLite)

```bash
# 1) Cloner le dépôt
git clone <VOTRE_URL_GITHUB_ICI>
cd <NOM_DU_DOSSIER_CLONÉ>

# 2) Créer et activer un venv (recommandé)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# .\venv\Scripts\activate  # Windows PowerShell

# 3) Installer les dépendances
pip install -U pip
pip install django djangorestframework djangorestframework-simplejwt drf-spectacular django-cors-headers python-dotenv

# 4) Migrations & superuser
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # créer un admin

# 5) Lancer le serveur
python manage.py runserver
```

Par défaut, **SQLite** stocke la base dans le fichier `db.sqlite3` à la racine du projet.

---

## Configuration rapide (extraits)

**softdesk/settings.py**
```python
INSTALLED_APPS = [
    # ...
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "users",
    "projects",
    "issues",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    # ...
]

AUTH_USER_MODEL = "users.User"  # Déclarer AVANT la première migration

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {"TITLE": "SoftDesk Support API", "VERSION": "1.0.0"}

TIME_ZONE = "Europe/Paris"
USE_TZ = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # front local (à ajuster si besoin)
]

# Base de données SQLite (par défaut)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

**softdesk/urls.py**
```python
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("api/v1/", include("projects.urls")),  # routes à imbriquer à l'étape suivante
]
```

**users/models.py** (utilisateur custom + champs RGPD)
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True)
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
```
> ⚠️ Garder `AUTH_USER_MODEL = "users.User"` avant la toute première migration.

---

## Démarrer un projet neuf (si vous partez de zéro)

```bash
mkdir softdesk-support-api && cd softdesk-support-api
git init
python3 -m venv venv && source venv/bin/activate
pip install django djangorestframework djangorestframework-simplejwt drf-spectacular django-cors-headers python-dotenv

django-admin startproject softdesk .
python manage.py startapp users
python manage.py startapp projects
python manage.py startapp issues

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Versionner sur GitHub

```bash
# Depuis la racine du projet (où se trouve manage.py)
git add .
git commit -m "chore: bootstrap with Django+DRF (SQLite, JWT, docs)"
git branch -M main
git remote add origin <URL_DU_REPO_GITHUB>
git push -u origin main
```

---

## Tests (à venir à l'étape 2+)
- Unitaires (serializers, permissions)
- Intégration (endpoints CRUD)
- Sécurité (accès non autorisés)
- RGPD (consentements, suppression compte)
- Performances (pagination)

## Licence
MIT (suggestion)
