from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from services.talks.models import Talk
from services.winners.models import DrawWinner
from services.students.models import Student
from services.speakers.models import Speaker
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo
import uuid

DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

class AdminRetrieveWinnerByTalkViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='password123'
        )
        self.client.login(username='admin', password='password123')

        self.speaker = Speaker.objects.create(
            name="Maria Silva",
            description="Especialista em IA",
            linkedin_link="in/maria",
            instagram_link="@maria",
            pronouns="ela/dela",
            role="Junior frontend developer"
        )

        datetime_now = dt.now(ZoneInfo('America/Sao_Paulo'))
        self.talk = Talk.objects.create(
            title='Introdução a Machine Learning',
            description='Aprenda o que é Machine Learning e quais técnicas aplicar em cada caso',
            start_time=datetime_now.strftime(DATETIME_FORMAT),
            end_time=(datetime_now + timedelta(hours=2)).strftime(DATETIME_FORMAT),
        )
        self.talk.speakers.add(self.speaker)

        self.url = reverse('admin-retrieve-winner-by-talk', kwargs={'talk_id': self.talk.id})

    def test_retrieve_draw_winners_by_talk(self):
        student1 = Student.objects.create(
            name="CO-SSI da Silva Junior",
            email="co-ssi.jr@usp.br",
            usp_number="281905",
            code="A001"
        )

        student2 = Student.objects.create(
            name="Ana Santos",
            email="ana.santos@usp.br",
            usp_number="281906",
            code="A002"
        )

        draw_winner1 = DrawWinner.objects.create(
            talk=self.talk,
            student=student1,
        )

        draw_winner2 = DrawWinner.objects.create(
            talk=self.talk,
            student=student2,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        expected_winner1 = {
            "id": draw_winner1.id,
            "code": student1.code,
            "name": student1.name,
            "email": student1.email,
            "talkTitle": self.talk.title,
        }

        expected_winner2 = {
            "id": draw_winner2.id,
            "code": student2.code,
            "name": student2.name,
            "email": student2.email,
            "talkTitle": self.talk.title,
        }

        self.assertCountEqual([expected_winner1, expected_winner2], response.data)

        for winner in response.data:
            # O front recebe os dados do estudante e da palestra, não os ids das relações
            self.assertEqual(set(winner.keys()), {"id", "code", "name", "email", "talkTitle"})
            self.assertNotIn("student", winner)
            self.assertNotIn("talk", winner)

    def test_retrieve_draw_winners_by_talk_not_found(self):
        fake_id = 404
        url_with_invalid_id = reverse('admin-retrieve-winner-by-talk', kwargs={'talk_id': fake_id})

        response = self.client.get(url_with_invalid_id)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_retrieve_draw_winners_by_talk_unauthorized(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
