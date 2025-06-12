from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from api.models import Speaker, Student
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
import uuid

class RetrieveSpeakerViewTestCase(APITestCase):
    def setUp(self):
        # Cria alguns palestrantes
        self.speaker1 = Speaker.objects.create(
            id=uuid.uuid4(),
            name="Maria Silva",
            description="Especialista em IA",
            social_media="@maria",
            pronouns="ela/dela",
            role="Junior frontend developer"
        )

        self.speaker2 = Speaker.objects.create(
            id=uuid.uuid4(),
            name="João Souza",
            description="Desenvolvedor Python",
            social_media="@joao",
            pronouns="ele/dele",
            role="Senior backend developer"
        )

        self.speaker3 = Speaker.objects.create(
            id=uuid.uuid4(),
            name="Ana Clara",
            description="Cientista de Dados",
            social_media="@clarinha",
            pronouns="ela/dela",
            role="Devops intern"
        )

        self.url = reverse('list-speakers')

    def test_retrieve_speakers(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        speaker1 = {
            "id": self.speaker1.id,
            "name": self.speaker1.name,
            "description": self.speaker1.description,
            "social_media": self.speaker1.social_media,
            "pronouns": self.speaker1.pronouns,
            "role": self.speaker1.role
        }

        speaker2 = {
            "id": self.speaker2.id,
            "name": self.speaker2.name,
            "description": self.speaker2.description,
            "social_media": self.speaker2.social_media,
            "pronouns": self.speaker2.pronouns,
            "role": self.speaker2.role
        }

        speaker3 = {
            "id": self.speaker3.id,
            "name": self.speaker3.name,
            "description": self.speaker3.description,
            "social_media": self.speaker3.social_media,
            "pronouns": self.speaker3.pronouns,
            "role": self.speaker3.role
        }

        self.assertDictEqual(speaker1, response.data[0])
        self.assertDictEqual(speaker2, response.data[1])
        self.assertDictEqual(speaker3, response.data[2])