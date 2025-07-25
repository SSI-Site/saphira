import uuid

from django.db import models

from services.students.models import Student
from services.gifts.models import Gift
from services.speakers.models import Speaker

class Talk(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128, unique=True)
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE)
    description = models.CharField(max_length=1024, null=True)
    start_time = models.DateTimeField(unique=True)
    end_time = models.DateTimeField(unique=True)

    def __str__(self) -> str:
        return f"Talk: {self.speaker.name} - '{self.title}'"

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

class DrawWinner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    talk = models.ForeignKey(Talk, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'talk',)

    def __str__(self) -> str:
        return f"Winner: {self.student} na palestra '{self.talk}'"
