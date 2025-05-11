from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.test import TestCase
from api.models import Student

class AdminListStudentsViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # cria admin
        self.admin_user = User.objects.create_superuser(
            username='adminSSI',
            email='admin@test.com',
            password='adminSSIpassword'
        )

        # cria estudantes
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

        # faz login do admin
        self.client.login(username='adminSSI', password='adminSSIpassword')

        # url tratada
        self.url = reverse('admin-list-students')

    def test_list_students_authenticated(self):
        # simula requisição para obter os estudantes
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verifica se os dois estudantes são retornados
        self.assertEqual(len(response.data), 2)

        # dados recebidos
        returned_ids = [str(student['id']) for student in response.data]
        returned_names = [student['name'] for student in response.data]
        returned_codes = [student['code'] for student in response.data]

        # verifica se os ids, nomes e códigos dos estudantes estão na resposta
        self.assertIn(str(self.student1.id), returned_ids)
        self.assertIn(str(self.student2.id), returned_ids)

        self.assertIn(self.student1.name, returned_names)
        self.assertIn(self.student2.name, returned_names)

        self.assertIn(self.student1.code, returned_codes)
        self.assertIn(self.student2.code, returned_codes)

    def test_list_students_unauthenticated(self):
        # desfaz o login do admin
        self.client.logout()

        # simula requisição sem autenticação
        response = self.client.get(self.url)

        # verifica se o código de status é 403
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
