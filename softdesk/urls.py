# softdesk/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Views internes
from users.views import SignupView, UserViewSet
from projects_app.views import (
    ProjectViewSet,
    ContributorViewSet,
    IssueViewSet,
    CommentViewSet,
)

# Auth JWT
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# OpenAPI schema
from drf_spectacular.views import SpectacularAPIView


# Router DRF
router = DefaultRouter()

# Users
router.register(r"auth/users", UserViewSet, basename="user")

# Projects / Contributors
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"contributors", ContributorViewSet, basename="contributor")

# Issues / Comments
router.register(r"issues", IssueViewSet, basename="issue")
router.register(r"comments", CommentViewSet, basename="comment")


urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # Auth JWT + Signup
    path("api/v1/auth/login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/auth/signup", SignupView.as_view(), name="auth-signup"),

    # API (toutes les routes enregistrées dans router)
    path("api/v1/", include(router.urls)),

    # Schéma OpenAPI (protégé par IsAuthenticated via settings)
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
]
