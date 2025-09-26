from rest_framework import serializers
from projects.models import Contributor
from .models import Issue, Comment

# Serializer de base pour Issue, avec une validation très simple
class IssueSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.id")  # l'auteur = request.user

    class Meta:
        model = Issue
        fields = [
            "id", "title", "description", "tag", "priority", "status",
            "project", "assignee", "author", "created_time"
        ]
        read_only_fields = ["id", "author", "created_time"]

    # Règle métier simple : si assignee est renseigné, il doit être contributeur du projet
    def validate(self, attrs):
        project = attrs.get("project") or getattr(self.instance, "project", None)
        assignee = attrs.get("assignee")
        if assignee and project:
            is_contrib = (project.author_id == assignee.id) or \
                         Contributor.objects.filter(project=project, user=assignee).exists()
            if not is_contrib:
                raise serializers.ValidationError("L'assignee doit être un contributeur du projet.")
        return attrs


# Serializer simple pour Comment
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.id")

    class Meta:
        model = Comment
        fields = ["id", "uuid", "description", "issue", "author", "created_time"]
        read_only_fields = ["id", "uuid", "author", "created_time"]
