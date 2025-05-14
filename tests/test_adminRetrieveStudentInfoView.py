import datetime
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient, APITestCase, force_authenticate

from api.models import Presence, Student, Talk

class AdminRetrieveStudentInfoViewTestCase(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="test_admin",
            email="foo@example.com",
            password="1234"
        )


    def test_valid_student_with_presence(self):
        """Testa o endpoint com dois estudantes. Um deles com presença e outro sem"""
        talk = Talk.objects.create(
            title="Palestra do Neymar",
            speaker="Neymar",
            description="A palestra do neymar",
            date_time=datetime.datetime.now()
        )

        student1 = Student.objects.create(
            name = "Glauber",
            email = "glauber@email.com",
            usp_number="023456789",
        )

        student2 = Student.objects.create(
            name = "Felipe",
            email = "felipe@email.com",
            usp_number="123456789",
        )

        # Presença do estudante 1
        Presence.objects.create(
            student=student1,
            talk=talk,
        )

        self.client.force_login(user=self.admin)
        response: Response = self.client.get(self.url(student1.usp_number), format="json")

        # Verifica se o estudante 1 tem presença
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], student1.id)
        self.assertEqual(response.data["name"], student1.name)
        self.assertIn("presences", response.data)
        self.assertEqual(len(response.data["presences"]), 1)
        self.assertEqual(response.data["presences"][0]["talk_title"], talk.title)

        response: Response = self.client.get(self.url(student2.usp_number), format="json")

        # Verifica se o estudante 2 não tem presença
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], student2.id)
        self.assertEqual(response.data["name"], student2.name)
        self.assertEqual(response.data.get("in_person_presences_count", 0), 0)
        self.assertIn("presences", response.data)
        self.assertEqual(response.data["presences"], [])

    # Retorna a url com o student_id
    # O student_id é o usp_number
    def url(self, id: int) -> str:
        return reverse("admin-retrieve-student-info", args=[id])
