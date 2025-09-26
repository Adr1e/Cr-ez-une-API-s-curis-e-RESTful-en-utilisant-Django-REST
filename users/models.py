from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Champs RGPD simples
    age = models.PositiveIntegerField(null=True, blank=True)         # âge (optionnel)
    can_be_contacted = models.BooleanField(default=False)            # consentement contact
    can_data_be_shared = models.BooleanField(default=False)          # consentement partage

    # AbstractUser fournit déjà username/email/password/first_name/last_name
    # Les validations (ex: âge ≥ 15) seront faites côté serializer d'inscription.
