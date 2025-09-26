from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project, Contributor, Issue, Comment

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    """Projection légère d'un utilisateur pour l'affichage imbriqué."""
    class Meta:
        model = User
        fields = ("id", "username", "email")


class ProjectSerializer(serializers.ModelSerializer):
    """Projet + auteur (lecture seule). Crée automatiquement l'entrée Contributor auteur."""
    author = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ("id", "name", "description", "type", "author", "created_at")
        read_only_fields = ("id", "author", "created_at")

    def create(self, validated_data):
        request = self.context.get("request")
        project = Project.objects.create(author=request.user, **validated_data)
        Contributor.objects.create(user=request.user, project=project, role=Contributor.ROLE_AUTHOR)
        return project


class ContributorSerializer(serializers.ModelSerializer):
    """Association user ↔ project (rôle). Empêche les doublons."""
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    user_detail = SimpleUserSerializer(source="user", read_only=True)

    class Meta:
        model = Contributor
        fields = ("id", "user", "user_detail", "project", "role", "created_at")
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        user = attrs.get("user")
        project = attrs.get("project")
        if Contributor.objects.filter(user=user, project=project).exists():
            raise serializers.ValidationError("Cet utilisateur est déjà contributeur de ce projet.")
        return attrs


class IssueSerializer(serializers.ModelSerializer):
    """Ticket d'un projet. L'auteur est toujours le request.user."""
    author = serializers.ReadOnlyField(source="author.id")

    class Meta:
        model = Issue
        fields = ["id", "title", "description", "tag", "priority", "status",
                  "project", "author", "assignee", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context["request"]
        project = attrs.get("project") or (self.instance and self.instance.project)
        project_id = project.id if project else None
        assignee = attrs.get("assignee") or (self.instance and self.instance.assignee)

        if project_id and not Contributor.objects.filter(user=request.user, project_id=project_id).exists():
            raise serializers.ValidationError("You must be a contributor of this project.")
        if assignee and project_id and not Contributor.objects.filter(user=assignee, project_id=project_id).exists():
            raise serializers.ValidationError("Assignee must be a contributor of the same project.")
        return attrs

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Commentaire rattaché à une issue du projet."""
    author = serializers.ReadOnlyField(source="author.id")

    class Meta:
        model = Comment
        fields = ["id", "issue", "author", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context["request"]
        issue = attrs.get("issue") or (self.instance and self.instance.issue)
        if issue and not Contributor.objects.filter(user=request.user, project=issue.project).exists():
            raise serializers.ValidationError("You must be a contributor of this project.")
        return attrs

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
