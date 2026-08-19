from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.urls import reverse
from django.test import TestCase
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo
from services.talks.models import Talk
from services.winners.models import DrawWinner
from services.students.models import Student
from services.speakers.models import Speaker

DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

class AdminListRetrieveWinnerViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.student1 = Student.objects.create(
            name='Aluno 01',
            email='aluno01@usp.br',
            usp_number='12345678',
            code='A001'
        )
        self.student2 = Student.objects.create(
            name='Aluno 02',
            email='aluno02@usp.br',
            usp_number='87654321',
            code='A002'
        )

        self.speaker1 = Speaker.objects.create(
            name='Palestrante 01',
            description='Palestrante teste 01',
            linkedin_link='in/pal_teste01',
            instagram_link='@pal_teste01',
            pronouns='ele/dele',
            role='Amazon intern'
        )
        self.speaker2 = Speaker.objects.create(
            name='Palestrante 02',
            description='Palestrante teste 02',
            linkedin_link='in/pal_teste02',
            instagram_link='@pal_teste02',
            pronouns='ela/dela',
            role='Google intern'
        )

        self.now = dt.now(ZoneInfo('America/Sao_Paulo'))
        self.talk1 = Talk.objects.create(
            title='Talk 01',
            description='Descricao 01',
            start_time=self.now.strftime(DATETIME_FORMAT),
            end_time=(self.now + timedelta(hours=1)).strftime(DATETIME_FORMAT)
        )
        self.talk1.speakers.add(self.speaker1)
        self.talk2 = Talk.objects.create(
            title='Talk 02',
            description='Descricao 02',
            start_time=(self.now + timedelta(days=1)).strftime(DATETIME_FORMAT),
            end_time=(self.now + timedelta(days=1) + timedelta(hours=1)).strftime(DATETIME_FORMAT)
        )
        self.talk2.speakers.add(self.speaker2)

        self.draw_winner1 = DrawWinner.objects.create(
            talk=self.talk1,
            student=self.student2,
        )
        self.draw_winner2 = DrawWinner.objects.create(
            talk=self.talk2,
            student=self.student1,
        )

        self.url = reverse('admin-list-draw-winners')

    def login_as_admin(self):
        User.objects.create_superuser(
            username='adminSSI',
            email='admin@test.com',
            password='adminSSIpassword'
        )
        self.client.login(username='adminSSI', password='adminSSIpassword')

    def expected_winner(self, draw_winner):
        """Monta o sorteado no formato esperado pelo front-end"""
        return {
            'id': draw_winner.id,
            'code': draw_winner.student.code,
            'name': draw_winner.student.name,
            'email': draw_winner.student.email,
            'talkTitle': draw_winner.talk.title,
        }

    def test_list_draw_winner_authenticated(self):
        self.login_as_admin()

        response = self.client.get(self.url)
        # Limpa a sessão
        self.client.logout()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)

        self.assertCountEqual(
            [self.expected_winner(self.draw_winner1), self.expected_winner(self.draw_winner2)],
            response.data
        )

    def test_list_draw_winner_returns_student_and_talk_data(self):
        self.login_as_admin()

        response = self.client.get(self.url)
        self.client.logout()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for winner in response.data:
            # O front recebe os dados do estudante e da palestra, não os ids das relações
            self.assertEqual(set(winner.keys()), {'id', 'code', 'name', 'email', 'talkTitle'})
            self.assertNotIn('student', winner)
            self.assertNotIn('talk', winner)

    def test_list_draw_winner_without_winners(self):
        DrawWinner.objects.all().delete()
        self.login_as_admin()

        response = self.client.get(self.url)
        self.client.logout()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_list_draw_winner_unauthenticated(self):
        # Assegura que não há login
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_draw_winner_unauthorized(self):
        # Cria o token para o estudante
        authenticating_student = self.student1
        refresh = RefreshToken.for_user(authenticating_student)
        access_token = str(refresh.access_token)

        # Adiciona o token no header de autenticação
        bearer = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        response = self.client.get(self.url, **bearer)
        # Logout necessário para limpar a sessão
        self.client.logout()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
