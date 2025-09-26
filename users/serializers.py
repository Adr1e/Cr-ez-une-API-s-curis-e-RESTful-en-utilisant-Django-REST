from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """CRUD protégé pour lire/modifier son propre profil (admin voit tous)."""
    class Meta:
        model = User
        fields = [
            "id","username","email","first_name","last_name",
            "age","can_be_contacted","can_data_be_shared",
            "is_staff","date_joined",
        ]
        read_only_fields = ["id","is_staff","date_joined"]

class SignupSerializer(serializers.ModelSerializer):
    """Inscription publique : on exige un mot de passe et on vérifie l'âge."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username","email","password","first_name","last_name",
            "age","can_be_contacted","can_data_be_shared",
        ]

    def validate_age(self, value):
        # RGPD : interdire l'inscription < 15 ans
        if value is not None and value < 15:
            raise serializers.ValidationError("Âge minimum requis : 15 ans.")
        return value

    def create(self, validated_data):
        # create_user => hash du mot de passe + champs obligatoires
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user
