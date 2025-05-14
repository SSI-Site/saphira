import datetime
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient, APITestCase, force_authenticate

from api.models import Presence, Student, Talk

class AdminDrawOnTalkTestCase(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="test_admin",
            email="foo@example.com",
            password="1234"
        )


    def test_invalid_talk(self):
        """Testa o endpoint com um id de palestra falso"""
        fake_id = 404
        self.client.force_login(user=self.admin)
        response: Response = self.client.get(self.url(fake_id), format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], f"Palestra com id {fake_id} não encontrada.")


    def test_valid_talk_no_presence(self):
        """Testa o endpoint com uma palestra valida mas sem presenças"""
        talk = Talk.objects.create(
            title="Palestra do Neymar",
            speaker="Neymar",
            description="A palestra do neymar",
            date_time=datetime.datetime.now()
        )

        self.client.force_login(user=self.admin)
        response: Response = self.client.get(self.url(talk.id), format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Nenhum estudante presente nesta palestra.")

    def test_valid_talk_presence(self):
        """Testa o endpoint com uma palestra valida mas com presenças"""
        talk = Talk.objects.create(
            title="Palestra do Neymar",
            speaker="Neymar",
            description="A palestra do neymar",
            date_time=datetime.datetime.now()
        )

        student = Student.objects.create(
            name = "Glauber",
            email = "glauber@email.com",
        )

        presence = Presence.objects.create(
            student=student,
            talk=talk,
        )

        self.client.force_login(user=self.admin)
        response: Response = self.client.get(self.url(talk.id), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            "student_name": student.name,
        })

    # Retorna a url com o talk_id
    def url(self, id: int) -> str:
        return reverse("admin-draw-on-talk", args=[id])
