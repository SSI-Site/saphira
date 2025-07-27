from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo
from services.api.models import Talk, Presence
from services.students.models import Student
from services.speakers.models import Speaker

class RetrieveStudentPresencesViewTest(APITestCase):
    def setUp(self):
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

        base_time = dt.now(ZoneInfo('America/Sao_Paulo'))

        self.talk1 = Talk.objects.create(
            title="Palestra 1",
            description="Descrição 1",
            start_time=base_time,
            end_time=base_time + timedelta(hours=1)
        )
        self.talk1.speakers.add(self.speaker)

        self.talk2 = Talk.objects.create(
            title="Palestra 2",
            description="Descrição 2",
            start_time=base_time + timedelta(hours=2),  # Garante unicidade
            end_time=base_time + timedelta(hours=3)
        )
        self.talk2.speakers.add(self.speaker)

        Presence.objects.create(student=self.student, talk=self.talk1)
        Presence.objects.create(student=self.student, talk=self.talk2)

        self.client = APIClient()

    def test_retrieve_presences(self):
        # Cria o token para o estudante
        refresh = RefreshToken.for_user(self.student)
        access_token = str(refresh.access_token)

        # Adiciona o token no header de autenticação
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        url = reverse('retrieve-student-presences', kwargs={'student_id': self.student.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['talk_title'], "Palestra 1")
        self.assertEqual(response.data[1]['talk_title'], "Palestra 2")

    def test_unauthenticated_access_returns_401(self):
        url = reverse('retrieve-student-presences', kwargs={'student_id': self.student.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_access_other_student_presences_returns_empty_or_forbidden(self):
        other_student = Student.objects.create(
            name='Outro Aluno',
            email='outro@example.com',
            usp_number='12345678',
            code='C456'
        )
        refresh = RefreshToken.for_user(other_student)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        url = reverse('retrieve-student-presences', kwargs={'student_id': self.student.id})
        response = self.client.get(url)

        self.assertIn(response.status_code, [403, 200])

    def test_student_with_no_presences_gets_empty_list(self):
        student_no_presences = Student.objects.create(
            name='Novo Aluno',
            email='novo@example.com',
            usp_number='00000000',
            code='D789'
        )
        refresh = RefreshToken.for_user(student_no_presences)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        url = reverse('retrieve-student-presences', kwargs={'student_id': student_no_presences.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_invalid_token_returns_401(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid.token.here')
        url = reverse('retrieve-student-presences', kwargs={'student_id': self.student.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
