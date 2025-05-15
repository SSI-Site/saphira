from api.models import Gift, Student, StudentGift
from django.test import TestCase

class GiftModelTestCase(TestCase):
    def test_create_gift(self):
        # Cria um objeto Gift e verifica se foi salvo corretamente
        gift = Gift.objects.create(
            name="Camiseta",
            description="Camiseta do evento",
            min_presence=2,
            total_amount=10,
            balance=10
        )
        # Verifica se o gift foi criado e os campos estão corretos
        self.assertIsNotNone(gift.id)
        self.assertEqual(gift.name, "Camiseta")
        self.assertEqual(gift.balance, 10)

class StudentGiftRelationTestCase(TestCase):
    def test_student_gift_relation(self):
        # Cria um estudante
        student = Student.objects.create(
            name="João",
            email="joao@email.com",
            usp_number="12345678"
        )
        # Cria um gift
        gift = Gift.objects.create(
            name="Chaveiro",
            description="Chaveiro do evento",
            min_presence=1,
            total_amount=5,
            balance=5
        )
        # Cria a relação entre estudante e gift
        student_gift = StudentGift.objects.create(
            student=student,
            gift=gift,
            received=True
        )
        # Verifica se a relação foi criada corretamente
        self.assertEqual(student_gift.student, student)
        self.assertEqual(student_gift.gift, gift)
        self.assertTrue(student_gift.received)
