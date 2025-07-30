from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from services.talks.models import Sponsor, Talk
from services.speakers.models import Speaker
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo

class AdminRetrieveUpdateDestroySponsorViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')

        self.sponsor = Sponsor.objects.create(
            name="Sponsor Original",
            url="https://original.com"
        )
        self.url = reverse('admin-retrieve-update-destroy-sponsor', kwargs={'pk': self.sponsor.pk})

    def test_retrieve_sponsor(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.sponsor.name)
        self.assertEqual(response.data["url"], self.sponsor.url)

    def test_update_sponsor(self):
        updated_data = {
            "name": "Sponsor Atualizado",
            "url": "https://atualizado.com"
        }
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Sponsor atualizado com sucesso.")
        self.assertEqual(response.data["sponsor"]["name"], updated_data["name"])
        self.assertEqual(response.data["sponsor"]["url"], updated_data["url"])
        self.sponsor.refresh_from_db()
        self.assertEqual(self.sponsor.name, updated_data["name"])
        self.assertEqual(self.sponsor.url, updated_data["url"])

    def test_partial_update_sponsor(self):
        response = self.client.patch(self.url, {"url": "https://newurl.com"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["sponsor"]["url"], "https://newurl.com")
        self.sponsor.refresh_from_db()
        self.assertEqual(self.sponsor.url, "https://newurl.com")

    def test_update_sponsor_invalid_data(self):
        response = self.client.put(self.url, {"name": "", "url": "invalid"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("url", response.data)

    def test_delete_sponsor_without_talks(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Sponsor removido com sucesso.")
        self.assertFalse(Sponsor.objects.filter(pk=self.sponsor.pk).exists())

    def test_delete_sponsor_with_talks_should_fail(self):
        speaker = Speaker.objects.create(
            name="Speaker",
            description="desc",
            social_media="@social",
            pronouns="ele/dele",
            role="palestrante"
        )
        now = dt.now(ZoneInfo("America/Sao_Paulo"))

        talk = Talk.objects.create(
            title="Palestra com Sponsor",
            description="Descrição",
            start_time=now,
            end_time=now + timedelta(hours=1),
            sponsor=self.sponsor
        )
        talk.speakers.add(speaker)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertTrue(Sponsor.objects.filter(pk=self.sponsor.pk).exists())

    def test_unauthenticated_user_cannot_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_user_cannot_update(self):
        self.client.logout()
        user = User.objects.create_user(username="user", password="userpass")
        self.client.login(username="user", password="userpass")

        response = self.client.patch(self.url, {"name": "Tentativa"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)