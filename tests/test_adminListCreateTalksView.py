from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils.timezone import now, timedelta

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

    def test_create_talk(self):
        data = {
            "title": "Palestra Teste",
            "speaker": "Palestrante",
            "description": "Descrição",
            "date_time": (now() + timedelta(days=1)).strftime(DATETIME_FORMAT)
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message"], "Palestra criada com sucesso.")
        self.assertIn("talk", response.data)

    def test_list_talks(self):
        Talk.objects.create(
            title="Palestra Existente",
            date_time=now() + timedelta(days=2)
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
            "date_time": "2024-13-32T25:70",
            "speaker": "Palestrante"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_duplicate_talk_title(self):
        Talk.objects.create(title="Palestra Existente", date_time=now() + timedelta(days=1))

        data = {
            "title": "Palestra Existente",
            "date_time": (now() + timedelta(days=2)).strftime(DATETIME_FORMAT),
            "speaker": "Palestrante",
            "description": "Descrição"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)