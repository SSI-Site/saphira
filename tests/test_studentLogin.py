from rest_framework.test import APITestCase, APIClient
from rest_framework.views import APIView
from django.urls import reverse
from services.students.models import Student
from rest_framework import status

from unittest.mock import patch
from services.students.views import StudentLogin

class StudentLoginViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('student-login')

        # Pular o decorator no método dispatch da view
        patcher = patch.object(StudentLogin, 'dispatch', lambda s, r, *a, **kw: APIView.dispatch(s, r, *a, **kw))
        self.addCleanup(patcher.stop)
        patcher.start()


    def test_existing_student_login_returns_tokens(self):
        student = Student.objects.create(
            name='Aluno Existente',
            email='aluno@example.com',
            code='ABC1',
            usp_number='12345678'
        )

        response = self.client.post(self.url, {
            'name': student.name,
            'email': student.email
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['id'], student.id)

    def test_new_student_registration_returns_tokens(self):
        response = self.client.post(self.url, {
            'name': 'Novo Aluno',
            'email': 'novo@example.com',
            'usp_number': '87654321'
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['email'], 'novo@example.com')
        self.assertEqual(response.data['usp_number'], '87654321')

        self.assertTrue(Student.objects.filter(email='novo@example.com').exists())

    def test_missing_required_fields_returns_400(self):
        response = self.client.post(self.url, {
            'name': 'Faltando Email'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())

        response = self.client.post(self.url, {
            'email': 'sem_nome@example.com'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())

    def test_usp_number_optional_on_registration(self):
        response = self.client.post(self.url, {
            'name': 'Aluno Sem USP',
            'email': 'semusp@example.com'
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['email'], 'semusp@example.com')
        self.assertIsNone(response.data['usp_number'])

        student = Student.objects.get(email='semusp@example.com')
        self.assertIsNone(student.usp_number)
