from django.db import models

from services.speakers.models import Speaker

# Create your models here.
class Talk(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128, unique=True)
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE)
    description = models.CharField(max_length=1024, null=True)
    start_time = models.DateTimeField(unique=True)
    end_time = models.DateTimeField(unique=True)

    def __str__(self) -> str:
        return f"Talk: {self.speaker.name} - '{self.title}'"
