from django.db import models

from services.speakers.models import Speaker

# Create your models here.

class TalkActivityType(models.TextChoices):
    WORKSHOP = 'WS', 'Workshop'
    PRESENTATION = 'PR', 'Presentation'

class Talk(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128, unique=True)
    speakers = models.ManyToManyField(Speaker, related_name='talks')
    description = models.CharField(max_length=1024, null=True)
    start_time = models.DateTimeField(unique=True)
    end_time = models.DateTimeField(unique=True)
    activity_type = models.CharField(max_length=2, choices=TalkActivityType.choices, default=TalkActivityType.PRESENTATION)

    def __str__(self) -> str:
        return f"Talk: '{self.title}'"
