from rest_framework import viewsets, permissions
from .models import Issue, Comment
from .serializers import IssueSerializer, CommentSerializer
from projects.permissions import IsProjectContributor, IsAuthorOrReadOnly

# Vue CRUD pour Issue (tickets)
class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectContributor & IsAuthorOrReadOnly]

    def get_queryset(self):
        # On liste les issues du projet passé dans l'URL
        return Issue.objects.select_related("project", "assignee", "author") \
                            .filter(project_id=self.kwargs.get("project_pk"))

    def perform_create(self, serializer):
        # L'auteur est l'utilisateur connecté ; le projet vient de l'URL
        serializer.save(author=self.request.user, project_id=self.kwargs["project_pk"])


# Vue CRUD pour Comment
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectContributor & IsAuthorOrReadOnly]

    def get_queryset(self):
        # On liste les comments de l'issue passée dans l'URL
        return Comment.objects.select_related("issue", "author", "issue__project") \
                              .filter(issue_id=self.kwargs.get("issue_pk"))

    def perform_create(self, serializer):
        # L'auteur est l'utilisateur connecté ; l'issue vient de l'URL
        serializer.save(author=self.request.user, issue_id=self.kwargs["issue_pk"])
