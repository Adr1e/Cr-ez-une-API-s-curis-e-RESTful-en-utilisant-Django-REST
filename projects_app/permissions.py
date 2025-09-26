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
    True si l'utilisateur est membre (Contributor) du projet.
    Utilise .exists() pour ne pas charger d'objets en mémoire.
    """
    return Contributor.objects.filter(user=user, project_id=project_id).exists()


class IsProjectAuthorOrReadOnly(BasePermission):
    """
    PROJETS
    - Lecture : autorisée aux utilisateurs authentifiés membres du projet
    - Écriture : réservée à l’auteur du projet
    """
    def has_object_permission(self, request, view, obj: Project):
        if request.method in SAFE_METHODS:
            return Contributor.objects.filter(project=obj, user=request.user).exists()
        return obj.author_id == request.user.id


class IsProjectAuthorForContributorWrite(BasePermission):
    """
    CONTRIBUTORS
    - Lecture : autorisée aux membres du projet
    - Création/Suppression/Modification : réservées à l’auteur du projet
      (la vérification finale est aussi faite en view.perform_create)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj: Contributor):
        if request.method in SAFE_METHODS:
            return Contributor.objects.filter(project=obj.project, user=request.user).exists()
        return obj.project.author_id == request.user.id


class IsProjectContributor(BasePermission):
    """
    GARDE 'MEMBRE DU PROJET' POUR TOUTES LES RESSOURCES DU PROJET

    - SAFE (GET/HEAD/OPTIONS) : utilisateur authentifié = OK
    - POST (création) : on exige que l'utilisateur soit contributor du projet ciblé
      * Issue : 'project' dans le body (ou query en fallback)
      * Comment : 'issue' dans le body (ou query) → on déduit le 'project'
    - Routes detail (retrieve/update/partial_update/destroy) :
      on délègue à has_object_permission qui lit le projet depuis l'objet.
    """
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        if request.method in SAFE_METHODS:
            return True

        # Sur les actions "detail" (update/partial_update/destroy), on laisse
        # has_object_permission valider l'appartenance via l'objet.
        if getattr(view, "action", None) in ("retrieve", "update", "partial_update", "destroy"):
            return True

        # Création (POST)
        project_id = None
        basename = getattr(view, "basename", "")

        if basename == "issue":
            project_id = request.data.get("project") or request.query_params.get("project")
        elif basename == "comment":
            issue_id = request.data.get("issue") or request.query_params.get("issue")
            if issue_id:
                try:
                    project_id = Issue.objects.only("project_id").get(pk=issue_id).project_id
                except Issue.DoesNotExist:
                    return False

        return bool(project_id) and is_contributor(user, project_id)

    def has_object_permission(self, request, view, obj):
        # Déduit project_id depuis l'objet manipulé
        if isinstance(obj, Issue):
            project_id = obj.project_id
        elif isinstance(obj, Comment):
            project_id = obj.issue.project_id
        elif isinstance(obj, Project):
            project_id = obj.id
        else:
            project = getattr(obj, "project", None)
            project_id = getattr(project, "id", None)

        return (
            request.user and request.user.is_authenticated
            and project_id is not None
            and is_contributor(request.user, project_id)
        )


class IsIssueAuthorOrStaff(BasePermission):
    """
    ISSUES — CONFORME CDC
    Écriture (PUT/PATCH/DELETE) autorisée uniquement :
      - à l'auteur de l'issue
      - ou au staff
    Lecture : autorisée (vérifiée en amont par IsProjectContributor)
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # obj est une Issue ici
        return getattr(obj, "author_id", None) == request.user.id or request.user.is_staff


class IsAuthorOrReadOnly(BasePermission):
    """
    Garde générique (utile pour Comment) :
    - Lecture autorisée pour tous (si déjà filtré par appartenance projet)
    - Écriture réservée à l’auteur de l’objet ou au staff
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff or getattr(obj, "author_id", None) == request.user.id
