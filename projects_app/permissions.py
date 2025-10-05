"""
Permissions pour l'app 'projects_app'.

Règles clés (CDC) :
- Accès aux ressources d'un projet réservé aux contributeurs du projet.
- Issue : seuls l'auteur de l'issue (ou staff) peut modifier/supprimer.
- Comment : seul l'auteur du commentaire (ou staff) peut modifier/supprimer.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Project, Contributor, Issue, Comment


def is_contributor(user, project_id) -> bool:
    """
    Indique si l'utilisateur appartient au projet.
    Utilise .exists() pour éviter de charger des objets en mémoire.
    """
    return Contributor.objects.filter(user=user, project_id=project_id).exists()


class IsProjectAuthorOrReadOnly(BasePermission):
    """
    Projets :
    - Lecture : autorisée à l'auteur ou à tout contributeur du projet.
    - Écriture : réservée à l'auteur du projet.
    """
    def has_object_permission(self, request, view, obj: Project):
        # Autorisations de lecture
        if request.method in SAFE_METHODS:
            # L'auteur peut toujours lire son projet
            if obj.author_id == request.user.id:
                return True
            # Sinon, il faut être contributeur du projet
            return Contributor.objects.filter(project=obj, user=request.user).exists()
        # Pour écrire, il faut être l'auteur
        return obj.author_id == request.user.id


class IsProjectAuthorForContributorWrite(BasePermission):
    """
    Contributeurs :
    - Lecture : permise aux membres du projet.
    - Création / Modification / Suppression : réservées à l'auteur du projet.
    """
    def has_permission(self, request, view):
        # L'utilisateur doit être authentifié
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj: Contributor):
        # Lecture : autorisée aux membres du projet
        if request.method in SAFE_METHODS:
            return Contributor.objects.filter(project=obj.project, user=request.user).exists()
        # Écriture : réservée à l'auteur du projet
        return obj.project.author_id == request.user.id


class IsProjectContributor(BasePermission):
    """
    Garde "membre du projet" pour Issues et Comments.

    - SAFE (GET/HEAD/OPTIONS) : utilisateur authentifié autorisé.
    - POST : l'utilisateur doit être contributeur du projet ciblé.
      * Issue : 'project' dans le body ou la query.
      * Comment : 'issue' dans le body ou la query, puis on déduit le projet.
    - Détail (retrieve/update/partial_update/destroy) :
      vérification via l'objet manipulé (has_object_permission).
    """
    def has_permission(self, request, view):
        user = request.user
        # Refus si utilisateur non authentifié
        if not (user and user.is_authenticated):
            return False

        # Lecture générale autorisée si authentifié
        if request.method in SAFE_METHODS:
            return True

        # Sur les actions "detail", on délègue à has_object_permission
        if getattr(view, "action", None) in ("retrieve", "update", "partial_update", "destroy"):
            return True

        # Création (POST) : contrôler l'appartenance au projet
        project_id = None
        basename = getattr(view, "basename", "")

        if basename == "issue":
            # On attend un project id dans le body ou la query
            project_id = request.data.get("project") or request.query_params.get("project")
        elif basename == "comment":
            # On récupère l'issue puis on déduit le projet
            issue_id = request.data.get("issue") or request.query_params.get("issue")
            if issue_id:
                try:
                    project_id = Issue.objects.only("project_id").get(pk=issue_id).project_id
                except Issue.DoesNotExist:
                    return False

        # Autorisé uniquement si l'utilisateur est contributeur du projet ciblé
        return bool(project_id) and is_contributor(user, project_id)

    def has_object_permission(self, request, view, obj):
        """
        Vérifie l'appartenance au projet à partir de l'objet (Issue/Comment/Project).
        """
        # Déduction du project_id selon le type de l'objet
        if isinstance(obj, Issue):
            project_id = obj.project_id
        elif isinstance(obj, Comment):
            project_id = obj.issue.project_id
        elif isinstance(obj, Project):
            project_id = obj.id
        else:
            project = getattr(obj, "project", None)
            project_id = getattr(project, "id", None)

        # Autorisé si authentifié et membre du projet
        return (
            request.user and request.user.is_authenticated
            and project_id is not None
            and is_contributor(request.user, project_id)
        )


class IsIssueAuthorOrStaff(BasePermission):
    """
    Issues :
    - Lecture : autorisée (contrôlée en amont par IsProjectContributor).
    - Écriture (PUT/PATCH/DELETE) : réservée à l'auteur de l'issue ou au staff.
    """
    def has_object_permission(self, request, view, obj):
        # Lecture toujours autorisée ici (barrière projet déjà passée)
        if request.method in SAFE_METHODS:
            return True
        # Écriture réservée à l'auteur de l'issue ou au staff
        return getattr(obj, "author_id", None) == request.user.id or request.user.is_staff


class IsAuthorOrReadOnly(BasePermission):
    """
    Garde générique (utilisée pour Comment) :
    - Lecture : autorisée.
    - Écriture : réservée à l'auteur de l'objet ou au staff.
    """
    def has_object_permission(self, request, view, obj):
        # Lecture toujours autorisée ici (barrière projet déjà passée)
        if request.method in SAFE_METHODS:
            return True
        # Écriture réservée à l'auteur de l'objet ou au staff
        return request.user.is_staff or getattr(obj, "author_id", None) == request.user.id
