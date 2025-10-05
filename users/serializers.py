from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la gestion du profil utilisateur.
    - Permet à un utilisateur de consulter ou modifier son propre compte.
    - Un administrateur peut voir tous les utilisateurs.
    """
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "age", "can_be_contacted", "can_data_be_shared",
            "is_staff", "date_joined",
        ]
        # Certains champs ne peuvent pas être modifiés
        read_only_fields = ["id", "is_staff", "date_joined"]


class SignupSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour l'inscription publique.
    - Exige un mot de passe.
    - Vérifie que l'utilisateur a au moins 15 ans (conformité RGPD).
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username", "email", "password", "first_name", "last_name",
            "age", "can_be_contacted", "can_data_be_shared",
        ]

    def validate_age(self, value):
        """
        Vérifie que l'âge saisi respecte la limite légale.
        """
        if value is not None and value < 15:
            raise serializers.ValidationError("Âge minimum requis : 15 ans.")
        return value

    def create(self, validated_data):
        """
        Crée un utilisateur en hachant le mot de passe avant sauvegarde.
        """
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user
