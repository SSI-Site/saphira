from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.test import TestCase
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo

from services.talks.models import Talk, TalkActivityType
from services.speakers.models import Speaker

DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

class AdminRetrieveUpdateDestroyTalkViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.now = dt.now(ZoneInfo('America/Sao_Paulo'))

        self.admin_user = User.objects.create_superuser(
            username='adminSSI',
            email='admin@test.com',
            password='adminSSIpassword'
        )

        self.speaker = Speaker.objects.create(
            name="Palestrante Teste",
            description="Descrição do palestrante",
            social_media="@palestranteteste",
            pronouns="ele/dele",
            role="Palestrante"
        )

        self.talk = Talk.objects.create(
            title="Palestra Teste",
            description="Descrição",
            start_time=self.now,
            end_time=self.now + timedelta(hours=1)
        )
        self.talk.speakers.add(self.speaker)

        self.client.login(username='adminSSI', password='adminSSIpassword')
        self.url = reverse('admin-retrieve-update-destroy-talk', kwargs={'pk': self.talk.pk})

    def test_retrieve_talk_authenticated_admin(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(response_data['title'], self.talk.title)
        self.assertEqual(response_data['description'], self.talk.description)
        self.assertListEqual(response_data['speakers'], [ str(speaker.id) for speaker in self.talk.speakers.all()] )

    def test_retrieve_talk_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_talk_authenticated_admin(self):
        updated_data = {
            "title": "Palestra Atualizada",
            "speakers": [self.speaker.id],
            "description": "Nova Descrição",
            "start_time": (self.now + timedelta(days=2)).strftime(DATETIME_FORMAT),
            "end_time": (self.now + timedelta(days=2, hours=1)).strftime(DATETIME_FORMAT)
        }

        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.talk.refresh_from_db()
        self.assertEqual(self.talk.title, updated_data['title'])
        self.assertIsNotNone(self.talk.speakers.first())

    def test_update_talk_invalid_data(self):
        invalid_data = {
            "title": "",
            "start_time": (self.now + timedelta(days=2)).strftime(DATETIME_FORMAT),
            "end_time": (self.now + timedelta(days=2, hours=1)).strftime(DATETIME_FORMAT)
        }

        response = self.client.put(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.json())

    def test_partial_update_talk_authenticated_admin(self):
        speaker = Speaker.objects.create(
            name="Palestrante Teste 2",
            description="Descrição do palestrante 2",
            social_media="@palestranteteste2",
            pronouns="ele/dele",
            role="Palestrante"
        )

        partial_data = {
            "speakers": [speaker.id],
            "description": "Descrição Modificada"
        }

        response = self.client.patch(self.url, partial_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.talk.refresh_from_db()
        self.assertEqual(self.talk.speakers.get(), speaker)
        self.assertEqual(self.talk.description, partial_data['description'])

    def test_delete_talk_authenticated_admin(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['message'], 'Palestra removida com sucesso.')
        self.assertFalse(Talk.objects.filter(pk=self.talk.pk).exists())

    def test_delete_talk_unauthenticated(self):
        self.client.logout()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_talk_not_found(self):
        invalid_url = reverse('admin-retrieve-update-destroy-talk', kwargs={'pk': 999})

        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        updated_data = {
            "title": "Inexistente",
            "speaker": self.speaker.id,
            "description": "Nada",
            "start_time": self.now.strftime(DATETIME_FORMAT),
            "end_time": (self.now + timedelta(hours=1)).strftime(DATETIME_FORMAT)
        }
        response = self.client.put(invalid_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_talk_activity_type(self):
        updated_data = {
            "title": "Palestra com tipo",
            "speakers": [self.speaker.id],
            "description": "Descrição com tipo",
            "start_time": (self.now + timedelta(days=1)).strftime(DATETIME_FORMAT),
            "end_time": (self.now + timedelta(days=1, hours=1)).strftime(DATETIME_FORMAT),
            "activity_type": "WS"
        }

        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.talk.refresh_from_db()
        self.assertEqual(self.talk.activity_type, "WS")

    def test_partial_update_activity_type(self):
        response = self.client.patch(self.url, {"activity_type": "WS"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.talk.refresh_from_db()
        self.assertEqual(self.talk.activity_type, "WS")

    def test_update_invalid_activity_type(self):
        data = {"activity_type": "INVALID_TYPE"}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("activity_type", response.json())