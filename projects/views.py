from django.db.models import Q
from rest_framework import viewsets, permissions
from .models import Project, Contributor
from .serializers import ProjectSerializer, ContributorSerializer
from .permissions import IsProjectContributor, IsAuthorOrReadOnly

# Vue CRUD pour Project
class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    # Auth obligatoire + être contributeur pour accéder à l'objet + auteur pour modifier/supprimer
    permission_classes = [permissions.IsAuthenticated, IsProjectContributor & IsAuthorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        # On ne liste que les projets visibles (où je suis auteur ou contributeur)
        return Project.objects.select_related("author").filter(
            Q(author=user) | Q(contributors__user=user)
        ).distinct()

    def perform_create(self, serializer):
        # L'auteur est automatiquement le user connecté
        project = serializer.save(author=self.request.user)
        # On ajoute aussi l'auteur comme Contributor (rôle AUTHOR)
        Contributor.objects.get_or_create(
            user=self.request.user, project=project, defaults={"role": "AUTHOR"}
        )


# Vue CRUD pour gérer les Contributors d'un projet
class ProjectContributorsViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectContributor & IsAuthorOrReadOnly]

    def get_queryset(self):
        # On filtre les contributors du projet indiqué dans l'URL
        project_id = self.kwargs["project_pk"]
        return Contributor.objects.select_related("user", "project").filter(project_id=project_id)

    def perform_create(self, serializer):
        # Le project est injecté depuis l'URL imbriquée
        serializer.save(project_id=self.kwargs["project_pk"])
