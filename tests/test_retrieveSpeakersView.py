from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from services.speakers.models import Speaker
import uuid

class RetrieveSpeakerViewTestCase(APITestCase):
    def setUp(self):
        # Cria alguns palestrantes
        self.speaker1 = Speaker.objects.create(
            id=str(uuid.uuid4()),
            name="Maria Silva",
            description="Especialista em IA",
            linkedin_link="in/mariasilva",
            instagram_link="@mariasilva",
            pronouns="ela/dela",
            role="Junior frontend developer"
        )

        self.speaker2 = Speaker.objects.create(
            id=str(uuid.uuid4()),
            name="João Souza",
            description="Desenvolvedor Python",
            linkedin_link="in/joao_souza",
            instagram_link="@joaosouza",
            pronouns="ele/dele",
            role="Senior backend developer"
        )

        self.speaker3 = Speaker.objects.create(
            id=str(uuid.uuid4()),
            name="Ana Clara",
            description="Cientista de Dados",
            linkedin_link="in/anaclara",
            instagram_link="@anaclara",
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
            "linkedin_link": self.speaker1.linkedin_link,
            "instagram_link": self.speaker1.instagram_link,
            "pronouns": self.speaker1.pronouns,
            "role": self.speaker1.role
        }

        speaker2 = {
            "id": self.speaker2.id,
            "name": self.speaker2.name,
            "description": self.speaker2.description,
            "linkedin_link": self.speaker2.linkedin_link,
            "instagram_link": self.speaker2.instagram_link,
            "pronouns": self.speaker2.pronouns,
            "role": self.speaker2.role
        }

        speaker3 = {
            "id": self.speaker3.id,
            "name": self.speaker3.name,
            "description": self.speaker3.description,
            "linkedin_link": self.speaker3.linkedin_link,
            "instagram_link": self.speaker3.instagram_link,
            "pronouns": self.speaker3.pronouns,
            "role": self.speaker3.role
        }

        self.assertDictEqual(speaker1, response.data[0])
        self.assertDictEqual(speaker2, response.data[1])
        self.assertDictEqual(speaker3, response.data[2])
