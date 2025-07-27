import uuid

from django.db import models

from services.students.models import Student
from services.gifts.models import Gift
from services.talks.models import Talk
from services.speakers.models import Speaker
from services.presences.models import Presence

# TODO: remover isso
class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    talk = models.ForeignKey(Talk, on_delete=models.CASCADE)
    code = models.CharField(max_length=8, unique=True)
    begin = models.DateTimeField()
    duration = models.IntegerField()

    def __str__(self) -> str:
        return f"Token: {self.code} - '{self.talk}'"
