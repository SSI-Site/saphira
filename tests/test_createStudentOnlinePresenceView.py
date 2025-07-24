from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from services.api.models import Talk, Token
from services.students.models import Student
from services.speakers.models import Speaker
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo

class CreateStudentOnlinePresenceViewTestCase(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="test_admin",
            email="foo@example.com",
            password="1234"
        )

        self.speaker = Speaker.objects.create(
            name="Palestrante Teste",
            description="Descrição do palestrante",
            social_media="@palestranteteste",
            pronouns="ele/dele",
            role="Palestrante"
        )

    def test_valid_student_with_presence(self):
        # Cria uma palestra
        talk = Talk.objects.create(
            title="Palestra do Neymar",
            speaker=self.speaker,
            description="A palestra do neymar",
            start_time=dt.now(ZoneInfo('America/Sao_Paulo')),
            end_time=dt.now(ZoneInfo('America/Sao_Paulo')) + timedelta(hours=1)
        )

        # Cria estudante
        student1 = Student.objects.create(
            name="Glauber",
            email="glauber@email.com",
            usp_number="023456789",
        )

        token = Token.objects.create(
            talk=talk,
            code="12345678",
            begin=dt.now(ZoneInfo('America/Sao_Paulo')),
            duration=60,
        )

        # Teste sem autenticação (deve falhar)
        response = self.client.post(self.url(student1.id), data={"token_code": token.code}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Faz login do estudante para obter o JWT
        refresh = RefreshToken.for_user(student1)
        access_token = refresh.access_token

        # Usa o JWT no header Authorization
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(self.url(student1.id), data={"token_code": token.code}, format="json")
        data = response.json()

        # Verifica se a presença foi criada
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["talk"], talk.id)
        self.assertEqual(str(data["student"]), str(student1.id))

        # Tenta criar a presença novamente
        response = self.client.post(self.url(student1.id), data={"token_code": token.code}, format="json")
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data["error"], "Presença já registrada nessa palestra.")

    def test_token_expirado(self):
        # Cria uma palestra
        talk = Talk.objects.create(
            title="Palestra Expirada",
            speaker=self.speaker,
            description="Palestra com token expirado",
            start_time=dt.now(ZoneInfo('America/Sao_Paulo'))  + timedelta(hours=1),
            end_time=dt.now(ZoneInfo('America/Sao_Paulo')) + timedelta(hours=2)
        )

        # Cria estudante
        student1 = Student.objects.create(
            name="Glauber",
            email="glauber@email.com",
            usp_number="023456789",
        )

        # Cria token já expirado (begin no passado, duração curta)
        token = Token.objects.create(
            talk=talk,
            code="87654321",
            begin=dt.now(ZoneInfo('America/Sao_Paulo')) - timedelta(minutes=10),
            duration=1,  # 1 minuto de duração, já expirado
        )

        # Faz login do estudante para obter o JWT
        refresh = RefreshToken.for_user(student1)
        access_token = refresh.access_token

        # Usa o JWT no header Authorization
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(self.url(student1.id), data={"token_code": token.code}, format="json")
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(data["error"], "Token expirado.")

    # Retorna a url com o student_id
    def url(self, student_id: str) -> str:
        return reverse("create-student-online-presence", args=[student_id])
