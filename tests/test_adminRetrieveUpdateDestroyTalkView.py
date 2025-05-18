from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from api.models import Talk

DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

class AdminRetrieveUpdateDestroyTalkViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_superuser(
            username='adminSSI',
            email='admin@test.com',
            password='adminSSIpassword'
        )

        self.talk = Talk.objects.create(
            title="Palestra Teste",
            speaker="Palestrante",
            description="Descrição",
            date_time=timezone.now() + timedelta(days=1)
        )

        self.client.login(username='adminSSI', password='adminSSIpassword')
        self.url = reverse('admin-retrieve-update-destroy-talk', kwargs={'pk': self.talk.pk})

    # Testes GET
    def test_retrieve_talk_authenticated_admin(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertEqual(response_data['title'], self.talk.title)
        self.assertEqual(response_data['speaker'], self.talk.speaker)
        self.assertEqual(response_data['description'], self.talk.description)

    def test_retrieve_talk_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Testes PUT
    def test_update_talk_authenticated_admin(self):
        updated_data = {
            "title": "Palestra Atualizada",
            "speaker": "Novo Palestrante",
            "description": "Nova Descrição",
            "date_time": (timezone.now() + timedelta(days=2)).strftime(DATETIME_FORMAT)
        }
        
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.talk.refresh_from_db()
        self.assertEqual(self.talk.title, updated_data['title'])
        self.assertEqual(self.talk.speaker, updated_data['speaker'])

    def test_update_talk_invalid_data(self):
        invalid_data = {
            "title": "",
            "date_time": (timezone.now() + timedelta(days=2)).strftime(DATETIME_FORMAT)
        }
        
        response = self.client.put(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.json())

    # Testes PATCH
    def test_partial_update_talk_authenticated_admin(self):
        partial_data = {
            "speaker": "Palestrante Modificado",
            "description": "Descrição Modificada"
        }
        
        response = self.client.patch(self.url, partial_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.talk.refresh_from_db()
        self.assertEqual(self.talk.speaker, partial_data['speaker'])
        self.assertEqual(self.talk.description, partial_data['description'])

    # Testes DELETE
    def test_delete_talk_authenticated_admin(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['message'], 'Palestra removida com sucesso.')
        self.assertFalse(Talk.objects.filter(pk=self.talk.pk).exists())

    def test_delete_talk_unauthenticated(self):
        self.client.logout()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Teste para recurso não encontrado
    def test_talk_not_found(self):
        invalid_url = reverse('admin-retrieve-update-destroy-talk', kwargs={'pk': 999})
        
        # Teste GET
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Teste PUT
        response = self.client.put(invalid_url, {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Teste DELETE
        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)