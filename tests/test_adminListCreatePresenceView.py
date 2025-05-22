from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.urls import reverse
from api.models import Student, Talk, Presence
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo

class AdminListCreatePresenceViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')

        self.student = Student.objects.create(
            name='Aluno',
            email='aluno@example.com',
            usp_number='12345678',
            code='A123'
        )

        self.talk = Talk.objects.create(
            title='Palestra de Teste',
            speaker='Palestrante',
            description='Descrição',
            start_time=dt.now(ZoneInfo('America/Sao_Paulo')),
            end_time=dt.now(ZoneInfo('America/Sao_Paulo')) + timedelta(hours=1)
        )

        self.url = reverse('admin-list-create-presence')

    def test_create_presence(self):
        data = {
            "student_document": "12345678",
            "talk": self.talk.id
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["student"], self.student.id)
        self.assertEqual(response.data["talk"], self.talk.id)

    def test_list_presences(self):
        Presence.objects.create(student=self.student, talk=self.talk)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_presence_invalid_student(self):
        data = {
            "student_document": "00000000",
            "talk": self.talk.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Estudante com documento 00000000 não encontrado.", str(response.data))

    def test_create_presence_invalid_talk(self):
        data = {
            "student_document": "12345678",
            "talk": 9999
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("talk", response.data)

    def test_duplicate_presence(self):
        Presence.objects.create(student=self.student, talk=self.talk)
        
        data = {
            "student_document": "12345678",
            "talk": self.talk.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Presença já registrada para o estudante com documento 12345678 nesta palestra.", response.data)

    def test_regular_user_cant_create_presence(self):
        user = User.objects.create_user(username="user", password="password123")
        self.client.login(username="user", password="password123")
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cant_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)