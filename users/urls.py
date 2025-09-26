from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import UserViewSet, SignupView

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("signup", SignupView.as_view(), name="auth-signup"),
]
urlpatterns += router.urls
