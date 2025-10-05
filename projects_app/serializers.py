from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project, Contributor, Issue, Comment

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    """
    Représentation légère d'un utilisateur.
    Utilisée pour imbriquer un auteur ou un contributeur sans tout le profil.
    """
    class Meta:
        model = User
        fields = ("id", "username", "email")


class ProjectSerializer(serializers.ModelSerializer):
    """
    Sérialiseur de projet.
    - L'auteur est en lecture seule et renvoyé via SimpleUserSerializer.
    - À la création, on associe automatiquement le créateur comme AUTHOR dans Contributor.
    """
    author = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ("id", "name", "description", "type", "author", "created_at")
        read_only_fields = ("id", "author", "created_at")

    def create(self, validated_data):
        """
        Crée un projet avec l'utilisateur courant comme auteur.
        Ajoute également une entrée Contributor avec le rôle AUTHOR.
        """
        request = self.context.get("request")
        project = Project.objects.create(author=request.user, **validated_data)
        Contributor.objects.create(user=request.user, project=project, role=Contributor.ROLE_AUTHOR)
        return project


class ContributorSerializer(serializers.ModelSerializer):
    """
    Sérialiseur de contributeur (lien user ↔ project).
    - Empêche les doublons user/projet.
    - Expose un résumé du user via user_detail.
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    user_detail = SimpleUserSerializer(source="user", read_only=True)

    class Meta:
        model = Contributor
        fields = ("id", "user", "user_detail", "project", "role", "created_at")
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        """
        Refuse l'ajout si l'utilisateur est déjà contributeur du projet.
        """
        user = attrs.get("user")
        project = attrs.get("project")
        if Contributor.objects.filter(user=user, project=project).exists():
            raise serializers.ValidationError("Cet utilisateur est déjà contributeur de ce projet.")
        return attrs


class IssueSerializer(serializers.ModelSerializer):
    """
    Sérialiseur d'issue.
    - L'auteur est toujours le request.user et reste en lecture seule côté client.
    - Valide que le créateur et l'assigné appartiennent au projet ciblé.
    """
    author = serializers.ReadOnlyField(source="author.id")

    class Meta:
        model = Issue
        fields = [
            "id", "title", "description", "tag", "priority", "status",
            "project", "author", "assignee", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def validate(self, attrs):
        """
        Règles de validation :
        - Le demandeur doit être contributeur du projet.
        - L'assigné doit aussi être contributeur du même projet.
        """
        request = self.context["request"]
        project = attrs.get("project") or (self.instance and self.instance.project)
        project_id = project.id if project else None
        assignee = attrs.get("assignee") or (self.instance and self.instance.assignee)

        # L'utilisateur courant doit appartenir au projet
        if project_id and not Contributor.objects.filter(user=request.user, project_id=project_id).exists():
            raise serializers.ValidationError("You must be a contributor of this project.")

        # L'assigné doit appartenir au même projet
        if assignee and project_id and not Contributor.objects.filter(user=assignee, project_id=project_id).exists():
            raise serializers.ValidationError("Assignee must be a contributor of the same project.")
        return attrs

    def create(self, validated_data):
        """
        Affecte automatiquement l'auteur depuis le contexte de la requête.
        """
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """
    Sérialiseur de commentaire.
    - L'auteur est imposé côté serveur.
    - Vérifie que l'utilisateur qui commente est bien contributeur du projet de l'issue.
    """
    author = serializers.ReadOnlyField(source="author.id")

    class Meta:
        model = Comment
        fields = ["id", "issue", "author", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def validate(self, attrs):
        """
        Refuse la création/modification si l'utilisateur n'est pas contributeur
        du projet auquel appartient l'issue ciblée.
        """
        request = self.context["request"]
        issue = attrs.get("issue") or (self.instance and self.instance.issue)
        if issue and not Contributor.objects.filter(user=request.user, project=issue.project).exists():
            raise serializers.ValidationError("You must be a contributor of this project.")
        return attrs

    def create(self, validated_data):
        """
        Affecte automatiquement l'auteur depuis le contexte de la requête.
        """
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
