from django.contrib.auth.models import User
from django.urls import reverse
from services.talks.models import Talk
from services.winners.models import DrawWinner
from services.students.models import Student
from services.speakers.models import Speaker
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo
from rest_framework.test import APITestCase
import uuid

class AdminDestroyWinnerViewTestCase(APITestCase):
    def setUp(self):
        # Cria um admin para autenticação
        self.admin = User.objects.create_superuser(username="admin", password="admin123", email="admin@email.com")
        self.client.force_login(self.admin)

    def test_delete_existing_winner(self):
        # Cria um estudante e um palestrante
        student = Student.objects.create(
            name='Aluno',
            email='aluno@example.com',
            usp_number='87654321',
            code='B123'
        )

        speaker = Speaker.objects.create(
            name="Palestrante Teste",
            description="Descrição do palestrante",
            linkedin_link="in/palestranteteste",
            instagram_link="@palestranteteste",
            pronouns="ele/dele",
            role="Palestrante"
        )

        talk = Talk.objects.create(
            title='Palestra',
            description='Descrição',
            start_time=dt.now(ZoneInfo('America/Sao_Paulo')),
            end_time=dt.now(ZoneInfo('America/Sao_Paulo')) + timedelta(hours=1)
        )
        talk.speakers.add(speaker)

        winner = DrawWinner.objects.create(
            student=student,
            talk=talk
        )

        url = reverse('admin-destroy-winner', kwargs={'winner_id': winner.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Vencedor removido com sucesso.')
        self.assertFalse(DrawWinner.objects.filter(id=winner.id).exists())

    def test_delete_nonexistent_winner(self):
        # Tenta deletar um vencedor que não existe
        fake_id = uuid.uuid4()
        url = reverse('admin-destroy-winner', kwargs={'winner_id': fake_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
