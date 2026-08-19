from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from services.talks.models import Talk
from services.presences.models import Presence
from services.winners.models import DrawWinner
from services.students.models import Student
from services.speakers.models import Speaker
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo
import uuid

DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

class AdminRetrieveWinnerByStudentViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='password123'
        )
        self.client.login(username='admin', password='password123')

        self.student = Student.objects.create(
            name="CO-SSI da Silva Junior",
            email="co-ssi.jr@usp.br",
            usp_number="281905",
            code="A001"
        )

        self.url = reverse('admin-retrieve-winner-by-student', kwargs={'student_id': self.student.id})

    def test_retrieve_draw_winners_by_student(self):
        speaker = Speaker.objects.create(
            name="Maria Silva",
            description="Especialista em IA",
            linkedin_link="in/maria",
            instagram_link="@maria",
            pronouns="ela/dela",
            role="Junior frontend developer"
        )

        datetime_now = dt.now(ZoneInfo('America/Sao_Paulo'))
        talk1 = Talk.objects.create(
            title='Introdução a Machine Learning',
            description='Aprenda o que é Machine Learning e quais técnicas aplicar em cada caso',
            start_time=datetime_now.strftime(DATETIME_FORMAT),
            end_time=(datetime_now + timedelta(hours=2)).strftime(DATETIME_FORMAT),
        )
        talk1.speakers.add(speaker)

        talk2 = Talk.objects.create(
            title='Técnica RandomForest',
            description='Como aplicar a técnica de RandomForest ao seu projeto de IA',
            start_time=(datetime_now + timedelta(days=1)).strftime(DATETIME_FORMAT),
            end_time=(datetime_now + timedelta(days=1, hours=2)).strftime(DATETIME_FORMAT),
        )
        talk2.speakers.add(speaker)

        _presence1 = Presence.objects.create(
            student=self.student,
            talk=talk1,
        )

        _presence2 = Presence.objects.create(
            student=self.student,
            talk=talk2,
        )

        draw_winner1 = DrawWinner.objects.create(
            talk=talk1,
            student=self.student,
        )

        draw_winner2 = DrawWinner.objects.create(
            talk=talk2,
            student=self.student,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        expected_winner1 = {
            "id": draw_winner1.id,
            "code": self.student.code,
            "name": self.student.name,
            "email": self.student.email,
            "talkTitle": talk1.title,
        }

        expected_winner2 = {
            "id": draw_winner2.id,
            "code": self.student.code,
            "name": self.student.name,
            "email": self.student.email,
            "talkTitle": talk2.title,
        }

        self.assertCountEqual([expected_winner1, expected_winner2], response.data)

        for winner in response.data:
            # O front recebe os dados do estudante e da palestra, não os ids das relações
            self.assertEqual(set(winner.keys()), {"id", "code", "name", "email", "talkTitle"})
            self.assertNotIn("student", winner)
            self.assertNotIn("talk", winner)

    def test_retrieve_draw_winners_by_student_invalid_id(self):
        fake_id = uuid.uuid4()
        url_with_invalid_id = reverse('admin-retrieve-winner-by-student', kwargs={'student_id': fake_id})

        response = self.client.get(url_with_invalid_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_retrieve_draw_winners_by_student_unauthorized(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
