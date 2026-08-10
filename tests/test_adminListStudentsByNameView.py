from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.test import TestCase
from services.students.models import Student

class AdminListStudentsByNameViewTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_superuser(
            username='adminSSI',
            email='admin@test.com',
            password='adminSSIpassword'
        )

        # Estudantes temporários: o TestCase desfaz tudo ao fim de cada teste
        self.ana = Student.objects.create(
            name='Ana Beatriz Souza',
            email='ana.souza@usp.br',
            usp_number='11111111',
            code='A001'
        )
        self.bruno = Student.objects.create(
            name='Bruno Silva',
            email='bruno.silva@usp.br',
            usp_number='22222222',
            code='A002'
        )
        self.carla = Student.objects.create(
            name='Carla Souza',
            email='carla.souza@usp.br',
            usp_number='33333333',
            code='A003'
        )
        # Nome em minúsculas, para testar a busca sem diferenciar maiúsculas
        self.ana_paula = Student.objects.create(
            name='ana paula',
            email='ana.paula@usp.br',
            usp_number='44444444',
            code='A004'
        )

        self.client.login(username='adminSSI', password='adminSSIpassword')

    def search_url(self, name):
        """Monta a URL de /admin/students/search/<name>"""
        return reverse('admin-list-students-by-name', kwargs={'name': name})

    def returned_names(self, response):
        return [student['name'] for student in response.data]

    def test_search_returns_only_matching_students(self):
        response = self.client.get(self.search_url('Souza'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        self.assertCountEqual(
            self.returned_names(response),
            [self.ana.name, self.carla.name]
        )

        # Quem não bate com a busca fica de fora
        self.assertNotIn(self.bruno.name, self.returned_names(response))

    def test_search_is_case_insensitive(self):
        # 'ANA' deve encontrar tanto 'Ana Beatriz Souza' quanto 'ana paula'
        response = self.client.get(self.search_url('ANA'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            self.returned_names(response),
            [self.ana.name, self.ana_paula.name]
        )

    def test_search_matches_partial_name(self):
        # Um pedaço no meio do nome também encontra o estudante
        response = self.client.get(self.search_url('eatriz'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.ana.name)

    def test_search_with_name_containing_spaces(self):
        response = self.client.get(self.search_url('Ana Beatriz'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.ana.name)

    def test_search_returns_expected_fields(self):
        response = self.client.get(self.search_url('Bruno'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        student = response.data[0]
        self.assertEqual(set(student.keys()), {'id', 'name', 'code', 'email'})

        self.assertEqual(str(student['id']), str(self.bruno.id))
        self.assertEqual(student['name'], self.bruno.name)
        self.assertEqual(student['code'], self.bruno.code)
        self.assertEqual(student['email'], self.bruno.email)

    def test_search_without_matches_returns_empty_list(self):
        response = self.client.get(self.search_url('Zacarias'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_search_with_no_students_in_database(self):
        Student.objects.all().delete()

        response = self.client.get(self.search_url('Souza'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_search_only_looks_at_the_name(self):
        # O e-mail não é considerado na busca, apenas o nome
        response = self.client.get(self.search_url(self.bruno.email))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_search_unauthenticated(self):
        self.client.logout()

        response = self.client.get(self.search_url('Souza'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], 'Acesso exclusivo da CO-SSI.')

    def test_search_authenticated_as_common_user(self):
        # Usuário logado, mas sem ser da CO-SSI
        User.objects.create_user(
            username='estudante',
            email='estudante@test.com',
            password='estudantepassword'
        )
        self.client.logout()
        self.client.login(username='estudante', password='estudantepassword')

        response = self.client.get(self.search_url('Souza'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], 'Acesso exclusivo da CO-SSI.')

    def test_search_without_name_is_not_found(self):
        # /admin/students/search/ (sem nome) não corresponde a nenhuma rota
        response = self.client.get('/admin/students/search/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
