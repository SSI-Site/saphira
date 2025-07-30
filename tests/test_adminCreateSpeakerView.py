from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from services.speakers.models import Speaker
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

class AdminCreateSpeakerViewTestCase(APITestCase):
    def setUp(self):
        # Cria um admin para autenticação
        self.admin = User.objects.create_superuser(username="admin", password="admin123", email="admin@email.com")
        self.client.force_login(self.admin)
        self.url = reverse('admin-create-speaker')

    def test_create_speaker(self):
        data = {
            "name": "Palestrante Teste",
            "description": "Descrição do palestrante",
            "social_media": "@palestranteteste",
            "pronouns": "ele/dele",
            "role": "Palestrante"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Speaker.objects.count(), 1)
        self.assertEqual(Speaker.objects.get().name, "Palestrante Teste")

    def test_create_speaker_invalid(self):
        data = {
            "name": "",
            "description": "Descrição do palestrante",
            "social_media": "@palestranteteste",
            "pronouns": "ele/dele",
            "role": "Palestrante"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Speaker.objects.count(), 0)
    def test_create_speaker_unauthenticated(self):
        self.client.logout()
        data = {
            "name": "Palestrante Teste",
            "description": "Descrição do palestrante",
            "social_media": "@palestranteteste",
            "pronouns": "ele/dele",
            "role": "Palestrante"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Speaker.objects.count(), 0)

    def test_create_speaker_missing_fields(self):
        data = {
            #"name": "Palestrante Teste",
            "description": "Descrição do palestrante",
            "social_media": "@PALESTRA",
            "pronouns": "ele/dele",
            "role": "Palestrante"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Speaker.objects.count(), 0)
