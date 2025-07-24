from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from services.api.models import Talk, Presence, DrawWinner
from services.students.models import Student
from services.speakers.models import Speaker
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo
import uuid

DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

class AdminListCreateWinnerTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='password123'
        )
        self.client.login(username='admin', password='password123')

        # Cria modelos que serão utilizados em mais de uma funcao
        self.student = Student.objects.create(
            id=uuid.uuid4(),
            name="Acabou a criatividade",
            email="foi-mal-guys@usp.br",
            usp_number="389245",
            code="A004"
        ) # Os estudantes abaixo sao mais legais

        self.speaker = Speaker.objects.create(
            id=uuid.uuid4(),
            name="Maria Silva",
            description="Especialista em IA",
            social_media="@maria",
            pronouns="ela/dela",
            role="Junior frontend developer"
        )

        datetime_now = dt.now(ZoneInfo('America/Sao_Paulo'))
        self.talk = Talk.objects.create(
            id=1,
            title='Introdução a Machine Learning',
            speaker=self.speaker,
            description='Aprenda o que é Machine Learning e quais técnicas aplicar em cada caso',
            start_time=datetime_now.strftime(DATETIME_FORMAT),
            end_time=(datetime_now + timedelta(hours=2)).strftime(DATETIME_FORMAT),
        )

        self.url = reverse('admin-list-create-winner', kwargs={'talk_id': self.talk.id})

    def test_list_draw_winners(self):
        student1 = Student.objects.create(
            id=uuid.uuid4(),
            name="CO-SSI da Silva Junior",
            email="cossi.jr@usp.br",
            usp_number="281905",
            code="A001"
        )

        student2 = Student.objects.create(
            id=uuid.uuid4(),
            name="Luciano Digiampetri",
            email="luciano.digi@usp.br",
            usp_number="64023",
            code="A002"
        )

        _presence1 = Presence.objects.create(
            id=uuid.uuid4(),
            student=student1,
            talk=self.talk,
        )

        _presence2 = Presence.objects.create(
            id=uuid.uuid4(),
            student=student2,
            talk=self.talk,
        )

        draw_winner1 = DrawWinner.objects.create(
            id=uuid.uuid4(),
            talk=self.talk,
            student=student1,
        )

        draw_winner2 = DrawWinner.objects.create(
            id=uuid.uuid4(),
            talk=self.talk,
            student=student2,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        draw_winner1 = {
            "id": draw_winner1.id,
            "student": draw_winner1.student.id,
            "talk": draw_winner1.talk.id,
        }

        draw_winner2 = {
            "id": draw_winner2.id,
            "student": draw_winner2.student.id,
            "talk": draw_winner2.talk.id,
        }

        self.assertDictEqual(draw_winner1, response.data[0])
        self.assertDictEqual(draw_winner2, response.data[1])

    def test_create_draw_winner(self):
        student = Student.objects.create(
            id=uuid.uuid4(),
            name="José do Ensino Médio",
            email="jem@usp.br",
            usp_number="00000001",
            code="A003"
        )

        _presence = Presence.objects.create(
            id=uuid.uuid4(),
            student=student,
            talk=self.talk,
        )

        response = self.client.post(self.url, data={"student": student.id})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(student.id, response.data['student'])
        self.assertEqual(self.talk.id, response.data['talk'])

    def test_list_draw_winner_unauthorized(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_draw_winner_invalid_talk(self):
        url_with_invalid_talk = reverse('admin-list-create-winner', kwargs={'talk_id': 0})
        response = self.client.get(url_with_invalid_talk)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_create_draw_winner_unauthorized(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_draw_winner_invalid_talk(self):
        url_with_invalid_talk = reverse('admin-list-create-winner', kwargs={'talk_id': 0})
        response = self.client.post(url_with_invalid_talk, data={"student": self.student.id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_create_draw_winner_invalid_student(self):
        response = self.client.post(self.url, data={"student": uuid.uuid4()})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_create_draw_winner_without_presence(self):
        response = self.client.post(self.url, data={"student": self.student.id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_create_draw_winner_already_won(self):
        response = self.client.post(self.url, data={"student": self.student.id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
