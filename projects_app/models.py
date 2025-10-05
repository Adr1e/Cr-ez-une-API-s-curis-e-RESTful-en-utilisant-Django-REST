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

    def __str__(self) :
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
    # Catégories possibles pour un ticket (bug, fonctionnalité ou tâche)
    class Tag(models.TextChoices):
        BUG = "BUG", "Bug"
        FEATURE = "FEATURE", "Feature"
        TASK = "TASK", "Task"

    # Niveaux de priorité d'une issue
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    # Statuts possibles d'une issue
    class Status(models.TextChoices):
        TODO = "TODO", "To do"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        DONE = "DONE", "Done"

    # Titre du ticket
    title = models.CharField(max_length=255)
    # Description facultative du ticket
    description = models.TextField(blank=True)
    # Type de ticket (bug, fonctionnalité, tâche)
    tag = models.CharField(max_length=16, choices=Tag.choices, default=Tag.BUG)
    # Priorité du ticket
    priority = models.CharField(max_length=16, choices=Priority.choices, default=Priority.MEDIUM)
    # Statut du ticket
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.TODO)

    # Projet auquel l'issue est rattachée
    project = models.ForeignKey("projects_app.Project", on_delete=models.CASCADE, related_name="issues")
    # Auteur ayant créé le ticket
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="issues_authored")
    # Utilisateur assigné à la résolution du ticket
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="issues_assigned")

    # Dates de création et de dernière mise à jour
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Trie les issues de la plus récente à la plus ancienne
        ordering = ["-created_at"]

    def __str__(self):
        # Représentation lisible d'une issue
        return f"[{self.project_id}] {self.title}"


class Comment(models.Model):
    # Issue à laquelle le commentaire est lié
    issue = models.ForeignKey("projects_app.Issue", on_delete=models.CASCADE, related_name="comments")
    # Auteur du commentaire
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments_authored")
    # Contenu du commentaire
    description = models.TextField()

    # Dates de création et de dernière mise à jour
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Trie les commentaires par ordre chronologique
        ordering = ["created_at"]

    def __str__(self):
        # Représentation lisible d'un commentaire
        return f"Comment #{self.pk} on issue {self.issue_id}"
