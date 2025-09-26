from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project, Contributor

User = get_user_model()

# Serializer simple pour Project
class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.id")  # on ne poste pas l'auteur à la main

    class Meta:
        model = Project
        fields = ["id", "name", "description", "type", "author", "created_time"]
        read_only_fields = ["id", "author", "created_time"]


# Serializer simple pour Contributor
class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ["id", "user", "project", "role"]
        read_only_fields = ["id", "project"]  # le project vient de l'URL imbriquée
