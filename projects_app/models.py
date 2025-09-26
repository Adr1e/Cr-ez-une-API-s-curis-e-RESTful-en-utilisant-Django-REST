from django.conf import settings
from django.db import models

# On réutilise le modèle User custom déclaré dans settings.AUTH_USER_MODEL
User = settings.AUTH_USER_MODEL


class Project(models.Model):
    # Types possibles d’un projet (exemples)
    FRONTEND = "FRONTEND"
    BACKEND = "BACKEND"
    IOS = "IOS"
    ANDROID = "ANDROID"

    TYPE_CHOICES = [
        (FRONTEND, "Frontend"),
        (BACKEND, "Backend"),
        (IOS, "iOS"),
        (ANDROID, "Android"),
    ]

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    # L’auteur (créateur) du projet
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.type})"


class Contributor(models.Model):
    # Rôles possibles
    ROLE_AUTHOR = "AUTHOR"
    ROLE_CONTRIBUTOR = "CONTRIBUTOR"

    ROLE_CHOICES = [
        (ROLE_AUTHOR, "Author"),
        (ROLE_CONTRIBUTOR, "Contributor"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contributions",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="contributors",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CONTRIBUTOR)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Un même user ne peut être ajouté qu’une fois à un projet
        unique_together = ("user", "project")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user} -> {self.project} [{self.role}]"


class Issue(models.Model):
    class Tag(models.TextChoices):
        BUG = "BUG", "Bug"
        FEATURE = "FEATURE", "Feature"
        TASK = "TASK", "Task"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    class Status(models.TextChoices):
        TODO = "TODO", "To do"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        DONE = "DONE", "Done"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    tag = models.CharField(max_length=16, choices=Tag.choices, default=Tag.BUG)
    priority = models.CharField(max_length=16, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.TODO)

    project = models.ForeignKey("projects_app.Project", on_delete=models.CASCADE, related_name="issues")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="issues_authored")
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="issues_assigned")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.project_id}] {self.title}"


class Comment(models.Model):
    issue = models.ForeignKey("projects_app.Issue", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments_authored")
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment #{self.pk} on issue {self.issue_id}"