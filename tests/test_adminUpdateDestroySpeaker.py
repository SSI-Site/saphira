from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from api.models import Speaker
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

class AdminUpdateDestroySpeakerViewTestCase(APITestCase):
    def setUp(self):
        # Cria um admin para autenticação
        self.admin = User.objects.create_superuser(username="admin", password="admin123", email="admin@email.com")
        self.client.force_login(self.admin)
        # Cria um palestrante
        self.speaker = Speaker.objects.create(
            id=uuid.uuid4(),
            name="Palestrante Teste",
        )
        self.url = reverse('admin-update-destroy-speaker', kwargs={'speaker_id': self.speaker.id})

    def test_update_speaker(self):
        # Atualiza campos do palestrante
        data = {
            "name": "Novo Nome",
            "description": "Nova descrição",
            "social_media": "@novonome",
            "pronouns": "ele/dele"
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.speaker.refresh_from_db()
        self.assertEqual(self.speaker.name, data["name"])
        self.assertEqual(self.speaker.description, data["description"])
        self.assertEqual(self.speaker.social_media, data["social_media"])
        self.assertEqual(self.speaker.pronouns, data["pronouns"])

    def test_delete_speaker(self):
        # Remove o palestrante
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Speaker.objects.filter(id=self.speaker.id).exists())