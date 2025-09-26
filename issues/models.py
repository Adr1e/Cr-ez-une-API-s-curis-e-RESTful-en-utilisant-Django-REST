from django.conf import settings
from django.db import models
from projects.models import Project
import uuid

# Une "Issue" = un ticket (bug/feature/tâche), avec priorité et statut
class Issue(models.Model):
    TAG_CHOICES = [("BUG", "Bug"), ("FEATURE", "Feature"), ("TASK", "Task")]
    PRIORITY_CHOICES = [("LOW", "Low"), ("MEDIUM", "Medium"), ("HIGH", "High")]
    STATUS_CHOICES = [("TO_DO", "To Do"), ("IN_PROGRESS", "In Progress"), ("FINISHED", "Finished")]

    title = models.CharField(max_length=128)                                     # Titre court
    description = models.TextField()                                            # Détails / contexte
    tag = models.CharField(max_length=16, choices=TAG_CHOICES)                  # Nature
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default="MEDIUM")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="TO_DO")

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issues")     # Projet lié
    assignee = models.ForeignKey(                                                           # Assigné (optionnel)
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_issues"
    )
    author = models.ForeignKey(                                                             # Créateur
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="authored_issues"
    )
    created_time = models.DateTimeField(auto_now_add=True)                                  # Date de création

    def __str__(self):
        return f"[{self.project}] {self.title}"


# Un commentaire sur une issue
class Comment(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)   # Identifiant public pratique
    description = models.TextField()                                          # Contenu du commentaire
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")  # Issue liée
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.issue}"
