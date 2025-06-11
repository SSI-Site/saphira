import uuid

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    email = models.EmailField(max_length=128, unique=True)
    usp_number = models.CharField(max_length=8, unique=True, null=True, blank=True)
    code = models.CharField(max_length=4, unique=True, null=True, blank=True)

class Speaker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=512, null=True)
    social_media = models.CharField(max_length=64, null=True)
    pronouns = models.CharField(max_length=16, null=True)
    role = models.CharField(max_length=64)

class Talk(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128, unique=True)
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE)
    description = models.CharField(max_length=1024, null=True)
    start_time = models.DateTimeField(unique=True)
    end_time = models.DateTimeField(unique=True)

class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    talk = models.ForeignKey(Talk, on_delete=models.CASCADE)
    code = models.CharField(max_length=8, unique=True)
    begin = models.DateTimeField()
    duration = models.IntegerField()

class Presence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    talk = models.ForeignKey(Talk, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'talk',)

class Gift(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256, null=True)
    min_presence = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    total_amount = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    balance = models.IntegerField(default=0) # Não tem validador pois é atualizado automaticamente. Se for negativo, precisam ser corrigidos manualmente.

class StudentGift(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE)
    received = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'gift',)

class DrawWinner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    talk = models.ForeignKey(Talk, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'talk',)
