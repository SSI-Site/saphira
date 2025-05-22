from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.urls import reverse
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo

from api.models import Talk

DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

class AdminListCreateTalksViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='password123'
        )
        self.client.login(username='admin', password='password123')
        self.url = reverse('admin-list-create-talks')
        self.now = dt.now(ZoneInfo('America/Sao_Paulo'))

    def test_create_talk(self):
        data = {
            "title": "Palestra Teste",
            "speaker": "Palestrante",
            "description": "Descrição",
            "start_time": self.now.strftime(DATETIME_FORMAT),
            "end_time": (self.now + timedelta(hours=1)).strftime(DATETIME_FORMAT)
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message"], "Palestra criada com sucesso.")
        self.assertIn("talk", response.data)

    def test_list_talks(self):
        Talk.objects.create(
            title="Palestra Existente",
            speaker="Palestrante",
            description="Descrição",
            start_time=self.now,
            end_time=self.now + timedelta(hours=1)
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Palestra Existente")

    def test_regular_user_cant_create_talk(self):
        user = User.objects.create_user(username="user", password="password123")
        self.client.login(username="user", password="password123")
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cant_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_create_talk_invalid_datetime_format(self):
        data = {
            "title": "Palestra Inválida",
            "start_time": "2024-13-32T25:70", 
            "end_time": "2024-13-32T26:70", 
            "speaker": "Palestrante"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_duplicate_talk_title_and_start_time(self):
        Talk.objects.create(
            title="Palestra Existente",
            speaker="Outro Palestrante",
            description="Descrição",
            start_time=self.now,
            end_time=self.now + timedelta(hours=1)
        )

        data = {
            "title": "Palestra Existente",
            "speaker": "Palestrante",
            "description": "Descrição",
            "start_time": self.now.isoformat(), 
            "end_time": (self.now + timedelta(hours=1)).isoformat()
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
