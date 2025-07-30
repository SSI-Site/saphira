import uuid

from django.db import models

class Speaker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=512, null=True)
    social_media = models.CharField(max_length=64, null=True)
    pronouns = models.CharField(max_length=16, null=True)
    role = models.CharField(max_length=64)

    def __str__(self) -> str:
        return f"Speaker: {self.name}"
