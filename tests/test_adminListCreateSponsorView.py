from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from services.talks.models import Sponsor

class AdminListCreateSponsorViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')
        self.url = reverse('admin-list-create-sponsors')

    def test_create_sponsor_valid_data(self):
        data = {
            "name": "OpenAI",
            "url": "https://openai.com"
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("message"), "Sponsor criado com sucesso.")
        self.assertIn("sponsor", response.data)
        sponsor_data = response.data["sponsor"]
        self.assertEqual(sponsor_data["name"], data["name"])
        self.assertEqual(sponsor_data["url"], data["url"])

    def test_create_sponsor_invalid_data(self):
        data = {
            "name": "",
            "url": "not-a-valid-url"
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("url", response.data)

    def test_list_sponsors(self):
        Sponsor.objects.create(name="Sponsor A", url="https://a.com")
        Sponsor.objects.create(name="Sponsor B", url="https://b.com")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "Sponsor A")
        self.assertEqual(response.data[0]["url"], "https://a.com")
        self.assertEqual(response.data[1]["name"], "Sponsor B")
        self.assertEqual(response.data[1]["url"], "https://b.com")

    def test_unauthenticated_user_cannot_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_user_cannot_create(self):
        self.client.logout()
        user = User.objects.create_user(username='user', password='userpass')
        self.client.login(username='user', password='userpass')

        data = {
            "name": "Unauthorized Sponsor",
            "url": "https://unauth.com"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
