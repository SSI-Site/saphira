from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.test import TestCase

class AdminLoginViewTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_superuser(
            username='adminSSI',
            email='admin@test.com',
            password='adminSSIpassword'
        )

        # Define a URL testada
        self.url = reverse('admin-login')
    
    def test_login_admin_sucess(self):
        #Dados de login corretos
        data = {
            'username': 'adminSSI',
            'password': 'adminSSIpassword'
        }

        # Simula uma requisição POST para a URL de login
        response = self.client.post(self.url, data, format='json')

        # Verifica se o status HTTP é 200 OK (login bem-sucedido)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Logado como admin...utilize seus poderes com moderação ;)')

    def test_login_admin_failure(self):
        #Dados de login incorretos
        data = {
            'username': 'adminSSI',
            'password': 'wrongpassword'
        }

        # Simula uma requisição POST com credenciais incorretas
        response = self.client.post(self.url, data, format='json')

        # Verifica se o status HTTP é 401 UNAUTHORIZED (login falhou)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Você não é da CO-SSI...')