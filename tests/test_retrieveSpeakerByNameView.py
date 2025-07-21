from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from services.api.models import Speaker
from services.students.models import Student
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
import uuid

class RetrieveSpeakerByNameViewTestCase(APITestCase):
    def setUp(self):
        # Cria alguns palestrantes
        self.speaker1 = Speaker.objects.create(
            id=uuid.uuid4(),
            name="Maria Silva",
            description="Especialista em IA",
            social_media="@maria",
            pronouns="ela/dela"
        )
        self.speaker2 = Speaker.objects.create(
            id=uuid.uuid4(),
            name="João Souza",
            description="Desenvolvedor Python",
            social_media="@joao",
            pronouns="ele/dele"
        )
        self.speaker3 = Speaker.objects.create(
            id=uuid.uuid4(),
            name="Maria Clara",
            description="Cientista de Dados",
            social_media="@clarinha",
            pronouns="ela/dela"
        )

    def test_retrieve_speaker_by_exact_name(self):
        url = reverse('retrieve-speaker-by-name', kwargs={'name': 'Maria Silva'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Maria Silva")

    def test_retrieve_speaker_by_partial_name(self):
        url = reverse('retrieve-speaker-by-name', kwargs={'name': 'Maria'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deve retornar as duas "Maria"
        names = [speaker['name'] for speaker in response.data]
        self.assertIn("Maria Silva", names)
        self.assertIn("Maria Clara", names)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_speaker_by_name_not_found(self):
        url = reverse('retrieve-speaker-by-name', kwargs={'name': 'Fulano'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)