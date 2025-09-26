from rest_framework.permissions import BasePermission, SAFE_METHODS
from projects.models import Project, Contributor
from issues.models import Issue, Comment

# Petit helper : vérifier si un user est contributeur (ou auteur) d'un projet
def user_is_contributor(user, project: Project) -> bool:
    if project.author_id == user.id:
        return True
    return Contributor.objects.filter(project=project, user=user).exists()


# Permission 1 : accès réservé aux contributeurs du projet
class IsProjectContributor(BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj peut être Project, Issue ou Comment → on retrouve le projet
        if isinstance(obj, Project):
            project = obj
        elif isinstance(obj, Issue):
            project = obj.project
        elif isinstance(obj, Comment):
            project = obj.issue.project
        else:
            return False
        return user_is_contributor(request.user, project)


# Permission 2 : seules les méthodes d'écriture sont limitées à l'auteur
# - lecture (GET, HEAD) autorisée si on a passé IsProjectContributor avant
class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True  # lecture ok
        # On récupère le champ author (présent sur Project? Issue? Comment?)
        author = getattr(obj, "author", None)
        return bool(author and author.id == request.user.id)
