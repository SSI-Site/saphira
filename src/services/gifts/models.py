import uuid

from django.core.validators import MinValueValidator
from django.db import models

class Gift(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256, null=True)
    min_presence = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    total_amount = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    @property
    def balance(self) -> int:
        from services.students.models import StudentGift
        received_gifts_count = StudentGift.objects.filter(gift=self.id, received=True).count()
        return self.total_amount - received_gifts_count

    def __str__(self) -> str:
        return f"Gift: {self.name}"
