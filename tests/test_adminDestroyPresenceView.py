from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.urls import reverse
from services.api.models import Talk, Presence, StudentGift
from services.speakers.models import Speaker
from services.students.models import Student
from services.gifts.models import Gift
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo

class AdminDestroyPresenceViewTestCase(TestCase):
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
            usp_number='87654321',
            code='B123'
        )

        self.speaker = Speaker.objects.create(
            name="Palestrante Teste",
            description="Descrição do palestrante",
            social_media="@palestranteteste",
            pronouns="ele/dele",
            role="Palestrante"
        )

        self.talk = Talk.objects.create(
            title='Palestra',
            speaker=self.speaker,
            description='Descrição',
            start_time=dt.now(ZoneInfo('America/Sao_Paulo')),
            end_time=dt.now(ZoneInfo('America/Sao_Paulo')) + timedelta(hours=1)
        )

        self.presence = Presence.objects.create(student=self.student, talk=self.talk)

        self.url = reverse(
            'admin-destroy-presence',
            kwargs={
                'student_document': self.student.usp_number,
                'talk_id': self.talk.id
            }
        )

    def test_delete_presence(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Presença removida com sucesso.')
        self.assertFalse(Presence.objects.filter(id=self.presence.id).exists())

    def test_delete_presence_not_found(self):
        self.presence.delete()

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Presença não registrada', response.data.get('detail', ''))

    def test_delete_student_not_found(self):
        url = reverse('admin-destroy-presence', kwargs={
            'student_document': '99999999',
            'talk_id': self.talk.id
        })

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Estudante com documento', response.data.get('detail', ''))

    def test_delete_presence_for_student_with_gift_that_now_is_not_eligible(self):
        # Cria um gift que exige 1 presença mínima
        gift = Gift.objects.create(
            name='Gift Teste',
            description='Descrição do gift',
            min_presence=1,
            total_amount=10,
            balance=10
        )

        # Atribui o gift ao aluno
        StudentGift.objects.create(student=self.student, gift=gift)

        # Remove a presença do aluno
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Presença removida com sucesso.')

        # Verifica se o aluno não tem mais o gift
        self.assertFalse(StudentGift.objects.filter(student=self.student, gift=gift).exists())

    def test_delete_presence_unauthorized_user(self):
        self.client.logout()

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403) 

