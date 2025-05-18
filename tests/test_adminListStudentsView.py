from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.test import TestCase
from api.models import Student

class AdminListStudentsViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_superuser(
            username='adminSSI',
            email='admin@test.com',
            password='adminSSIpassword'
        )

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

        self.client.login(username='adminSSI', password='adminSSIpassword')

        self.url = reverse('admin-list-students')

    def test_list_students_authenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)

        returned_ids = [str(student['id']) for student in response.data]
        returned_names = [student['name'] for student in response.data]
        returned_codes = [student['code'] for student in response.data]

        self.assertIn(str(self.student1.id), returned_ids)
        self.assertIn(str(self.student2.id), returned_ids)

        self.assertIn(self.student1.name, returned_names)
        self.assertIn(self.student2.name, returned_names)

        self.assertIn(self.student1.code, returned_codes)
        self.assertIn(self.student2.code, returned_codes)

    def test_list_students_unauthenticated(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)