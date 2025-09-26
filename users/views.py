from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, generics
from .serializers import UserSerializer, SignupSerializer

User = get_user_model()

class IsSelfOrAdmin(permissions.BasePermission):
    """Un user voit/modifie seulement son propre compte. Admin voit tout."""
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or (obj.id == request.user.id)

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]

    def get_queryset(self):
        user = self.request.user
        return User.objects.all() if user.is_staff else User.objects.filter(id=user.id)

class SignupView(generics.CreateAPIView):
    """Endpoint public d'inscription : /api/v1/auth/signup"""
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]
