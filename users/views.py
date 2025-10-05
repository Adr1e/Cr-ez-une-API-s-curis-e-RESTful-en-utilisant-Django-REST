from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, generics
from .serializers import UserSerializer, SignupSerializer

User = get_user_model()


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Un utilisateur ne peut accéder ou modifier que son propre compte.
    - Un administrateur (is_staff) peut accéder à tous les comptes.
    """
    def has_object_permission(self, request, view, obj):
        # Autorise l'accès si l'utilisateur est admin ou s'il agit sur son propre profil
        return request.user.is_staff or (obj.id == request.user.id)


class UserViewSet(viewsets.ModelViewSet):
    """
    Vue pour la gestion des utilisateurs.
    - Lecture et modification limitées à soi-même.
    - Les administrateurs peuvent voir et gérer tous les comptes.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]

    def get_queryset(self):
        """
        Retourne la liste des utilisateurs accessible selon le rôle :
        - Admin : tous les comptes.
        - Utilisateur standard : uniquement son propre profil.
        """
        user = self.request.user
        return User.objects.all() if user.is_staff else User.objects.filter(id=user.id)


class SignupView(generics.CreateAPIView):
    """
    Vue d'inscription publique.
    Accessible sans authentification via :
    POST /api/v1/auth/signup
    """
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]
