from django.db import models
import uuid

from services.gifts.models import Gift

# Create your models here.
class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    email = models.EmailField(max_length=128, unique=True)
    usp_number = models.CharField(max_length=8, unique=True, null=True, blank=True)
    code = models.CharField(max_length=4, unique=True, null=True, blank=True)

    def __str__(self) -> str:
        return f"Student: {self.name}"

class StudentGift(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE)
    received = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'gift',)

    def __str__(self) -> str:
        return f"StudentGift: {self.student} - {self.gift}, recebido = {self.received}"