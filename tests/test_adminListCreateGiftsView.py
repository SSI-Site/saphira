from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from services.api.models import Speaker
from django.contrib.auth.models import User
from services.gifts.models import Gift
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

class AdminListCreateGiftsViewTestCase(APITestCase):
    def setUp(self):
        # Cria um admin para autenticação
        self.admin = User.objects.create_superuser(username="admin", password="admin123", email="admin@email.com")
        self.client.force_login(self.admin)
        self.url = reverse('admin-list-create-gifts')

    def test_create_gift(self):
        data = {
            "name": "Brinde Teste",
            "description": "Descrição do brinde",
            "min_presence": 1,
            "total_amount": 10
        }
        response = self.client.post(self.url, data, format="json")
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['name'], "Brinde Teste")
        self.assertEqual(data['description'], "Descrição do brinde")
        self.assertEqual(data['min_presence'], 1)
        self.assertEqual(data['total_amount'], 10)
        self.assertEqual(data['balance'], 10)

    def test_create_gift_invalid(self):
        data = {
            "name": "",
            "description": "Descrição do brinde",
            "min_presence": 1,
            "total_amount": 10
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_gift_unauthenticated(self):
        self.client.logout()
        data = {
            "name": "Brinde Teste",
            "description": "Descrição do brinde",
            "min_presence": 1,
            "total_amount": 10
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_gift_missing_fields(self):
        data = {
            "description": "Descrição do brinde",
            "min_presence": 1,
            "total_amount": 10
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_gift_wrong_type(self):
        data = {
            "name": "Brinde Teste",
            "description": "Descrição do brinde",
            "min_presence": "um",
            "total_amount": 10
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_gift_negative_amount(self):
        data = {
            "name": "Brinde Teste",
            "description": "Descrição do brinde",
            "min_presence": 1,
            "total_amount": -10
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_List_gifts(self):
        data = {
            "name": "Brinde Teste",
            "description": "Descrição do brinde",
            "min_presence": 1,
            "total_amount": 10
        }
        response = self.client.post(self.url, data, format="json")

        response = self.client.get(self.url + "?name=" + data['name'], format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Brinde Teste")