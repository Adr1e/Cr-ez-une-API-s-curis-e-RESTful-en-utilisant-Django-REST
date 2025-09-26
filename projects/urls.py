from rest_framework_nested import routers
from .views import ProjectViewSet, ProjectContributorsViewSet
from issues.views import IssueViewSet, CommentViewSet

# Router principal : /projects
router = routers.SimpleRouter()
router.register(r"projects", ProjectViewSet, basename="project")

# Routes imbriquées : /projects/{id}/users et /projects/{id}/issues
projects_router = routers.NestedSimpleRouter(router, r"projects", lookup="project")
projects_router.register(r"users", ProjectContributorsViewSet, basename="project-users")
projects_router.register(r"issues", IssueViewSet, basename="project-issues")

# Routes imbriquées niveau 2 : /projects/{id}/issues/{id}/comments
issues_router = routers.NestedSimpleRouter(projects_router, r"issues", lookup="issue")
issues_router.register(r"comments", CommentViewSet, basename="issue-comments")

# On expose tout
urlpatterns = router.urls + projects_router.urls + issues_router.urls
