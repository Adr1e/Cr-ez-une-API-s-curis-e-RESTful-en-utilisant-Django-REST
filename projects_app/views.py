from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied, NotFound
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
    """
    Gestion des projets.
    - Liste : renvoie les projets dont l'utilisateur est auteur ou contributeur.
    - Détail : 403 si l'utilisateur n'est ni auteur ni contributeur.
    - Création/édition/suppression : réservées à l'auteur (voir permissions).
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description", "type"]

    def get_queryset(self):
        """
        Retourne les projets visibles par l'utilisateur.
        Utilise une union auteur + contributeur.
        Prefetch des contributeurs pour limiter les requêtes.
        """
        user = self.request.user
        qs_author = Project.objects.filter(author=user)
        qs_contrib = Project.objects.filter(contributors__user=user)
        return qs_author.union(qs_contrib).distinct().prefetch_related("contributors")

    def get_object(self):
        """
        Récupère l'objet sans filtrer par le queryset personnalisé,
        puis applique un contrôle d'accès objet (403 si non autorisé).
        """
        lookup = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        try:
            obj = Project.objects.get(**{self.lookup_field: lookup})
        except Project.DoesNotExist:
            raise NotFound("Projet introuvable.")
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        """
        L'auteur est affecté côté serializer (ProjectSerializer.create).
        """
        serializer.save()


class ContributorViewSet(viewsets.ModelViewSet):
    """
    Gestion des contributeurs d'un projet.
    - Liste : visible pour les membres du projet.
    - Ajout/suppression : réservées à l'auteur du projet.
    """
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectAuthorForContributorWrite]

    def get_queryset(self):
        """
        Renvoie les contributeurs des projets dont l'utilisateur est membre.
        select_related pour charger user et project en une requête.
        Filtre optionnel par ?project=<id>.
        """
        user = self.request.user
        qs = (
            Contributor.objects.select_related("user", "project")
            .filter(project__contributors__user=user)
            .distinct()
        )
        project_id = self.request.query_params.get("project")
        return qs.filter(project_id=project_id) if project_id else qs

    def get_object(self):
        """
        Récupère un contributeur, sinon 404.
        Vérifie ensuite les permissions objet (403 si non autorisé).
        """
        lookup = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        try:
            obj = Contributor.objects.get(**{self.lookup_field: lookup})
        except Contributor.DoesNotExist:
            raise NotFound("Contributeur introuvable.")
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        """
        Autorise l'ajout uniquement si l'utilisateur est l'auteur du projet.
        """
        project = serializer.validated_data["project"]
        if project.author_id != self.request.user.id:
            raise PermissionDenied("Seul l’auteur du projet peut ajouter des contributeurs.")
        serializer.save()


class IssueViewSet(viewsets.ModelViewSet):
    """
    Gestion des issues (tickets).
    - Liste : uniquement pour les projets où l'utilisateur est contributeur.
    - Détail : 403 si l'utilisateur n'est pas membre du projet parent.
    - Écriture : réservée à l'auteur de l'issue ou au staff.
    """
    queryset = Issue.objects.select_related("project", "author", "assignee")
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectContributor, IsIssueAuthorOrStaff]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["created_at", "priority", "status"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        """
        Filtre par ?project=<id> si fourni.
        Restreint aux issues visibles par l'utilisateur (membre du projet).
        """
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs.filter(project__contributors__user=self.request.user).distinct()

    def get_object(self):
        """
        Charge une issue (avec relations) ou renvoie 404.
        Vérifie ensuite les permissions objet (403 si non autorisé).
        """
        lookup = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        try:
            obj = Issue.objects.select_related("project", "author", "assignee").get(**{self.lookup_field: lookup})
        except Issue.DoesNotExist:
            raise NotFound("Issue introuvable.")
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        """
        Affecte automatiquement l'auteur de l'issue à l'utilisateur courant.
        """
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Gestion des commentaires.
    - Liste : commentaires des issues appartenant à des projets où l'utilisateur est contributeur.
    - Détail : 403 si l'utilisateur n'est pas membre du projet parent.
    - Écriture : réservée à l'auteur du commentaire ou au staff.
    """
    queryset = Comment.objects.select_related("issue", "author", "issue__project")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectContributor, IsAuthorOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        """
        Filtre par ?issue=<id> si fourni.
        Restreint aux commentaires liés à des projets où l'utilisateur est membre.
        """
        qs = super().get_queryset()
        issue_id = self.request.query_params.get("issue")
        if issue_id:
            qs = qs.filter(issue_id=issue_id)
        return qs.filter(issue__project__contributors__user=self.request.user).distinct()

    def get_object(self):
        """
        Charge un commentaire (avec relations) ou renvoie 404.
        Vérifie ensuite les permissions objet (403 si non autorisé).
        """
        lookup = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        try:
            obj = Comment.objects.select_related("issue", "author", "issue__project").get(**{self.lookup_field: lookup})
        except Comment.DoesNotExist:
            raise NotFound("Commentaire introuvable.")
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        """
        Affecte automatiquement l'auteur du commentaire à l'utilisateur courant.
        """
        serializer.save(author=self.request.user)
