import uuid

from django.db import models

from services.students.models import Student
from services.gifts.models import Gift
from services.talks.models import Talk
from services.speakers.models import Speaker


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    talk = models.ForeignKey(Talk, on_delete=models.CASCADE)
    code = models.CharField(max_length=8, unique=True)
    begin = models.DateTimeField()
    duration = models.IntegerField()

    def __str__(self) -> str:
        return f"Token: {self.code} - '{self.talk}'"

class Presence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    talk = models.ForeignKey(Talk, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'talk',)

    def __str__(self) -> str:
        return f"Presence: {self.student} na palestra '{self.talk}'"