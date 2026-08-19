import uuid
from typing import override

from django.urls import reverse
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from services.students.models import (  # pyright: ignore[reportImplicitRelativeImport]
    Student,
)


class TestStudentProfile(APITestCase):
    @override
    def setUp(self) -> None:
        self.student = Student.objects.create(  # pyright: ignore[reportUninitializedInstanceVariable]
            name="Luiz SSI",
            email="luiz.ssi@gmail.com",
            usp_number="87654321",
            code="X0X",
        )

    def force_authentication(self, user):
        """Força a autenticação do usuário criando um fake refresh/access token"""
        refresh = RefreshToken.for_user(user)  # pyright: ignore[reportArgumentType]
        access_token = str(refresh.access_token)  # pyright: ignore[reportAttributeAccessIssue]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_get_own_student_profile_success(self):
        url = reverse("student-retrieve-update", kwargs={"student_id": self.student.pk})

        self.force_authentication(self.student)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.student.name)
        self.assertEqual(response.data["email"], self.student.email)
        self.assertEqual(response.data["usp_number"], self.student.usp_number)
        self.assertEqual(response.data["code"], self.student.code)
        self.assertEqual(
            parse_datetime(response.data["created_at"]), self.student.created_at
        )
        self.assertEqual(
            parse_datetime(response.data["updated_at"]), self.student.updated_at
        )

    def test_try_to_access_different_student_profile_failure(self):
        # Usa um uuid diferente do usuário logado.
        url = reverse(
            "student-retrieve-update", kwargs={"student_id": str(uuid.uuid4())}
        )
        self.force_authentication(self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_forbidden_student_profile_failure(self):
        url = reverse(
            "student-retrieve-update", kwargs={"student_id": str(uuid.uuid4())}
        )
        # NOTE: não autentica para checar se a rota tem um auth middleware
        # self.force_authentication(self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_own_student_profile_success(self):
        url = reverse("student-retrieve-update", kwargs={"student_id": self.student.pk})
        self.force_authentication(self.student)
        new_usp_number = "12345678"
        response = self.client.patch(url, {"usp_number": new_usp_number})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["usp_number"], new_usp_number)
        self.assertGreater(
            parse_datetime(response.data["updated_at"]), self.student.updated_at
        )

    def test_update_readonly_field_student_profile_failure(self):
        url = reverse("student-retrieve-update", kwargs={"student_id": self.student.pk})
        self.force_authentication(self.student)
        response = self.client.patch(url, {"code": "000"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], self.student.code)
