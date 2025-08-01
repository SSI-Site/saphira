from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from services.speakers.models import Speaker
from django.contrib.auth.models import User
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
            "linkedin_link": "in/novonome",
            "instagram_link": "@novonome",
            "pronouns": "ele/dele"
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.speaker.refresh_from_db()
        self.assertEqual(self.speaker.name, data["name"])
        self.assertEqual(self.speaker.description, data["description"])
        self.assertEqual(self.speaker.linkedin_link, data["linkedin_link"])
        self.assertEqual(self.speaker.instagram_link, data["instagram_link"])
        self.assertEqual(self.speaker.pronouns, data["pronouns"])

    def test_update_speaker_not_found(self):
        # Tenta atualizar um palestrante que não existe
        fake_id = uuid.uuid4()
        url = reverse('admin-update-destroy-speaker', kwargs={'speaker_id': fake_id})
        data = {
            "name": "Nome Inexistente",
            "description": "Descrição",
            "linkedin_link": "in/inexistente",
            "instagram_link": "@inexistente",
            "pronouns": "ele/dele"
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_speaker(self):
        # Remove o palestrante
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Speaker.objects.filter(id=self.speaker.id).exists())

    def test_delete_speaker_not_found(self):
        # Tenta deletar um palestrante que não existe
        fake_id = uuid.uuid4()
        url = reverse('admin-update-destroy-speaker', kwargs={'speaker_id': fake_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
