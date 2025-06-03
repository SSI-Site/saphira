from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.urls import reverse
from api.models import Gift, Student, StudentGift, Talk, Presence
from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo

class AdminListCreatePresenceViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')

        self.student = Student.objects.create(
            name='Aluno',
            email='aluno@example.com',
            usp_number='12345678',
            code='A123'
        )

        self.talk = Talk.objects.create(
            title='Palestra de Teste',
            speaker='Palestrante',
            description='Descrição',
            start_time=dt.now(ZoneInfo('America/Sao_Paulo')),
            end_time=dt.now(ZoneInfo('America/Sao_Paulo')) + timedelta(hours=1)
        )

        self.url = reverse('admin-list-create-presence')

    def test_create_presence(self):
        data = {
            "student_document": "12345678",
            "talk": self.talk.id
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["student"], self.student.id)
        self.assertEqual(response.data["talk"], self.talk.id)

    def test_list_presences(self):
        Presence.objects.create(student=self.student, talk=self.talk)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_presence_invalid_student(self):
        data = {
            "student_document": "00000000",
            "talk": self.talk.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Estudante com documento 00000000 não encontrado.", str(response.data))

    def test_create_presence_invalid_talk(self):
        data = {
            "student_document": "12345678",
            "talk": 9999
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("talk", response.data)

    def test_duplicate_presence(self):
        Presence.objects.create(student=self.student, talk=self.talk)
        
        data = {
            "student_document": "12345678",
            "talk": self.talk.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Presença já registrada para o estudante com documento 12345678 nesta palestra.", response.data)

    def test_regular_user_cant_create_presence(self):
        user = User.objects.create_user(username="user", password="password123")
        self.client.login(username="user", password="password123")
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cant_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

class StudentGiftAssignmentAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Cria admin e faz login
        self.admin = User.objects.create_superuser(username='admin', email='admin@email.com', password='adminpass')
        self.client.login(username='admin', password='adminpass')

        # Cria estudante
        self.student = Student.objects.create(
            name="Teste",
            email="teste@email.com",
            usp_number="12345678"
        )
        # Cria palestras
        base_time = dt.now(ZoneInfo('America/Sao_Paulo'))
        self.talks = [
            Talk.objects.create(
                title=f"Palestra {i}",
                speaker=f"Palestrante {i}",
                description=f"Descrição {i}",
                start_time=base_time + timedelta(hours=i*2),
                end_time=base_time + timedelta(hours=i*2+1)
            ) for i in range(3)
        ]
        # Cria brindes
        self.gift1 = Gift.objects.create(
            name="Chaveiro",
            description="Gift 1",
            min_presence=1,
            total_amount=10,
            balance=10
        )
        self.gift2 = Gift.objects.create(
            name="Camiseta",
            description="Gift 2",
            min_presence=2,
            total_amount=5,
            balance=5
        )
        self.url = reverse('admin-list-create-presence')

    def test_gift_assignment_by_presence(self):
        # Recebe gift1 na primeira presença
        response = self.client.post(self.url, {"student_document": self.student.usp_number, "talk": self.talks[0].id}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(StudentGift.objects.filter(student=self.student, gift=self.gift1).exists())
        self.assertFalse(StudentGift.objects.filter(student=self.student, gift=self.gift2).exists())

        # Recebe gift2 na segunda presença
        response = self.client.post(self.url, {"student_document": self.student.usp_number, "talk": self.talks[1].id}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(StudentGift.objects.filter(student=self.student, gift=self.gift2).exists())

        # Verifica que o gift1 não foi duplicado
        gifts = StudentGift.objects.filter(student=self.student)
        self.assertEqual(gifts.count(), 2)
        self.assertTrue(gifts.filter(gift=self.gift1).exists())
        self.assertTrue(gifts.filter(gift=self.gift2).exists())

    def test_no_duplicate_gift_assignment(self):
        # Garante que não recebe o mesmo gift duas vezes
        self.client.post(self.url, {"student_document": self.student.usp_number, "talk": self.talks[0].id}, format='json')
        self.client.post(self.url, {"student_document": self.student.usp_number, "talk": self.talks[0].id}, format='json')
        gifts = StudentGift.objects.filter(student=self.student, gift=self.gift1)
        self.assertEqual(gifts.count(), 1)

    def test_no_gift_when_criteria_not_met(self):
        # Cria um estudante sem presença suficiente para nenhum gift
        student2 = Student.objects.create(
            name="Sem Presença",
            email="sempresenca@email.com",
            usp_number="99999999"
        )
        # Não registra presença
        self.assertFalse(StudentGift.objects.filter(student=student2).exists())