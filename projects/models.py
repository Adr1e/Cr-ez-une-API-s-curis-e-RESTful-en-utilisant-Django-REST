from django.conf import settings
from django.db import models

# Un projet appartient à un auteur et a un type (backend, frontend, iOS, Android)
class Project(models.Model):
    TYPE_CHOICES = [
        ("backend", "Back-end"),
        ("frontend", "Front-end"),
        ("iOS", "iOS"),
        ("Android", "Android"),
    ]

    name = models.CharField(max_length=128)                                             # Nom du projet
    description = models.TextField(blank=True)                                         # Description courte
    type = models.CharField(max_length=16, choices=TYPE_CHOICES, default="backend")    # Type du projet
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_projects"
    )                                                                                  # Auteur (créateur)
    created_time = models.DateTimeField(auto_now_add=True)                             # Date de création

    def __str__(self):
        return self.name


# Lien entre un user et un projet (avec un rôle simple)
class Contributor(models.Model):
    ROLE_CHOICES = [("AUTHOR", "Author"), ("CONTRIBUTOR", "Contributor")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)       # Le compte utilisateur
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="contributors")
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default="CONTRIBUTOR")

    class Meta:
        unique_together = ("user", "project")  # Un utilisateur ne peut être ajouté qu'une fois

    def __str__(self):
        return f"{self.user} → {self.project} ({self.role})"
