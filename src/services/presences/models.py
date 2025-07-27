from django.db import models
import uuid

from services.students.models import Student
from services.talks.models import Talk

# Create your models here.
class Presence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    talk = models.ForeignKey(Talk, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'talk',)

    def __str__(self) -> str:
        return f"Presence: {self.student} na palestra '{self.talk}'"
