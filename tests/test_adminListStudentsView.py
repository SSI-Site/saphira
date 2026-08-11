from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.test import TestCase
from services.students.models import Student

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

    def create_students(self, quantity, first_index=3):
        """Cria estudantes extras, nomeados na mesma sequência dos criados no setUp"""
        return Student.objects.bulk_create([
            Student(
                name=f'Aluno {index:02d}',
                email=f'aluno{index:02d}@usp.br',
                usp_number=f'{index:08d}',
                code=f'B{index:03d}'
            )
            for index in range(first_index, first_index + quantity)
        ])

    def test_list_students_authenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

        students = response.data['results']
        self.assertEqual(len(students), 2)

        returned_ids = [str(student['id']) for student in students]
        returned_names = [student['name'] for student in students]
        returned_codes = [student['code'] for student in students]

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

    def test_list_students_authenticated_as_common_user(self):
        # Usuário logado, mas sem ser da CO-SSI
        User.objects.create_user(
            username='estudante',
            email='estudante@test.com',
            password='estudantepassword'
        )
        self.client.logout()
        self.client.login(username='estudante', password='estudantepassword')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], 'Acesso exclusivo da CO-SSI.')

    def test_list_students_without_students(self):
        Student.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_list_students_returns_every_student(self):
        Student.objects.create(
            name='Aluno 03',
            email='aluno03@usp.br',
            usp_number='11223344',
            code='A003'
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Student.objects.count())

    def test_list_students_returns_expected_fields(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for student in response.data:
            self.assertEqual(set(student.keys()), {'id', 'email', 'name', 'code'})
    def test_list_students_with_size(self):
        self.create_students(3)  # 5 estudantes no total

        response = self.client.get(self.url, {'size': 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

        # A lista é ordenada por nome, então a primeira página traz os dois primeiros alunos
        self.assertEqual(
            [student['name'] for student in response.data['results']],
            ['Aluno 01', 'Aluno 02']
        )

    def test_list_students_with_page(self):
        self.create_students(3)  # 5 estudantes no total

        first_page = self.client.get(self.url, {'size': 2, 'page': 1})
        second_page = self.client.get(self.url, {'size': 2, 'page': 2})

        self.assertEqual(second_page.status_code, status.HTTP_200_OK)
        self.assertEqual(second_page.data['count'], 5)
        self.assertEqual(len(second_page.data['results']), 2)
        self.assertIsNotNone(second_page.data['previous'])

        self.assertEqual(
            [student['name'] for student in second_page.data['results']],
            ['Aluno 03', 'Aluno 04']
        )

        # Páginas diferentes não repetem estudantes
        first_page_ids = {student['id'] for student in first_page.data['results']}
        second_page_ids = {student['id'] for student in second_page.data['results']}
        self.assertFalse(first_page_ids & second_page_ids)

    def test_list_students_last_page(self):
        self.create_students(3)  # 5 estudantes no total

        response = self.client.get(self.url, {'size': 2, 'page': 3})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIsNone(response.data['next'])

    def test_list_students_page_out_of_range(self):
        response = self.client.get(self.url, {'size': 2, 'page': 99})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_students_default_page_size(self):
        self.create_students(30)  # 32 estudantes no total

        response = self.client.get(self.url)

        self.assertEqual(response.data['count'], 32)
        self.assertEqual(len(response.data['results']), 20)

    def test_list_students_size_is_limited_to_max_page_size(self):
        self.create_students(120)  # 122 estudantes no total

        response = self.client.get(self.url, {'size': 500})

        self.assertEqual(response.data['count'], 122)
        self.assertEqual(len(response.data['results']), 100)
