from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo
from django.urls import reverse

from services.api.models import Talk, Token, Speaker
from services.api.utils import generate_token_code

DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

class ListCreateTokenViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='password123'
        )
        self.client.login(username='admin', password='password123')

        self.speaker = Speaker.objects.create(
            name="Palestrante Teste",
            description="Descrição do palestrante",
            social_media="@palestranteteste",
            pronouns="ele/dele",
            role="Palestrante"
        )

        self.talk = Talk.objects.create(
            title="Teste Palestra",
            speaker=self.speaker,
            start_time=dt.now(ZoneInfo('America/Sao_Paulo')),
            end_time=dt.now(ZoneInfo('America/Sao_Paulo')) + timedelta(hours=1)
        )

        self.url = reverse('admin-list-create-tokens')

    def test_create_token(self):
        data = {
            "talk": self.talk.id,
            "begin":  (dt.now(ZoneInfo('America/Sao_Paulo')) + timedelta(hours=2)).strftime(DATETIME_FORMAT),
            "duration": 45
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message"], "Token criado com sucesso.")
        self.assertIn("code", response.data["token"])

    def test_list_tokens(self):
        Token.objects.create(
            talk=self.talk,
            begin=dt.now(ZoneInfo('America/Sao_Paulo')),
            duration=30,
            code=generate_token_code()
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['talk'], self.talk.id)
        self.assertIn('begin', response.data[0])

    def test_unauthenticated_user_cant_create_token(self):
        self.client.logout()
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 403)

    def test_regular_user_cant_access(self):
        user = User.objects.create_user(username='user', password='pass')
        self.client.login(username='user', password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_token_code_format(self):
        data = {
            "talk": self.talk.id,
            "begin": (self.talk.start_time + timedelta(hours=1)).strftime(DATETIME_FORMAT),
            "duration": 45
        }
        response = self.client.post(self.url, data, format='json')
        code = response.data["token"]["code"]
        self.assertTrue(code.isalnum())
        self.assertEqual(len(code), 5)