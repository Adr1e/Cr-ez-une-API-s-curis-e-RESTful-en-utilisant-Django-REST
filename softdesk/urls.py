# softdesk/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import des vues
from users.views import SignupView, UserViewSet
from projects_app.views import (
    ProjectViewSet,
    ContributorViewSet,
    IssueViewSet,
    CommentViewSet,
)

# Authentification JWT
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Schéma OpenAPI
from drf_spectacular.views import SpectacularAPIView


# Configuration du routeur principal DRF
router = DefaultRouter()

# Routes liées aux utilisateurs
router.register(r"auth/users", UserViewSet, basename="user")

# Routes liées aux projets et contributeurs
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"contributors", ContributorViewSet, basename="contributor")

# Routes liées aux issues et commentaires
router.register(r"issues", IssueViewSet, basename="issue")
router.register(r"comments", CommentViewSet, basename="comment")


urlpatterns = [
    # Accès à l'administration Django
    path("admin/", admin.site.urls),

    # Authentification JWT et inscription
    path("api/v1/auth/login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/auth/signup", SignupView.as_view(), name="auth-signup"),

    # Inclusion des routes générées par le routeur
    path("api/v1/", include(router.urls)),

    # Endpoint pour le schéma OpenAPI (utilisé pour la documentation)
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
]
