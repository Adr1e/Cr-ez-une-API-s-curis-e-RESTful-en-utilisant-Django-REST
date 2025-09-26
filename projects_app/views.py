from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q

from .models import Project, Contributor, Issue, Comment
from .serializers import ProjectSerializer, ContributorSerializer, IssueSerializer, CommentSerializer
from .permissions import (
    IsProjectAuthorOrReadOnly,
    IsProjectAuthorForContributorWrite,
    IsProjectContributor,
    IsAuthorOrReadOnly,
    IsIssueAuthorOrStaff,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """CRUD des projets.
    - Liste restreinte aux projets dont l'utilisateur est auteur ou contributeur.
    - Écriture réservée à l'auteur du projet (permission IsProjectAuthorOrReadOnly).
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description", "type"]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(Q(contributors__user=user) | Q(author=user)).distinct()

    def perform_create(self, serializer):
        serializer.save()


class ContributorViewSet(viewsets.ModelViewSet):
    """Gestion des contributeurs d'un projet.
    - Lecture : membres du projet.
    - Ajout/suppression : auteur du projet uniquement.
    """
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectAuthorForContributorWrite]

    def get_queryset(self):
        user = self.request.user
        qs = Contributor.objects.filter(project__contributors__user=user).distinct()
        project_id = self.request.query_params.get("project")
        return qs.filter(project_id=project_id) if project_id else qs

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        if project.author_id != self.request.user.id:
            raise PermissionDenied("Seul l’auteur du projet peut ajouter des contributeurs.")
        serializer.save()


class IssueViewSet(viewsets.ModelViewSet):
    """Tickets (issues) d'un projet.
    - Accès réservé aux contributeurs du projet.
    - Écriture : auteur de l’issue (ou staff) uniquement.
    """
    queryset = Issue.objects.select_related("project", "author", "assignee")
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectContributor, IsIssueAuthorOrStaff]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["created_at", "priority", "status"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs.filter(project__contributors__user=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """Commentaires d'une issue.
    - Accès réservé aux contributeurs du projet parent.
    - Écriture : auteur du commentaire (ou staff) uniquement.
    """
    queryset = Comment.objects.select_related("issue", "author", "issue__project")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectContributor, IsAuthorOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        issue_id = self.request.query_params.get("issue")
        if issue_id:
            qs = qs.filter(issue_id=issue_id)
        return qs.filter(issue__project__contributors__user=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
