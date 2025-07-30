import uuid

from django.core.validators import MinValueValidator
from django.db import models

class Gift(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256, null=True)
    min_presence = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    total_amount = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    balance = models.IntegerField(default=0) # Não tem validador pois é atualizado automaticamente. Se for negativo, precisam ser corrigidos manualmente.

    def __str__(self) -> str:
        return f"Gift: {self.name}"