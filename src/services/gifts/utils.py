from services.api.models import Presence
from .models import Gift
from ..students.models import Student, StudentGift

def update_gift_balance (gift):
    # Obtém o número de alunos que possuem esse Gift
    students_count = StudentGift.objects.filter(gift=gift).count()
    # Atualiza o saldo do Gift
    gift.balance = students_count
    gift.save()

def check_and_assign_gifts(student):
    # Contar presenças do aluno
    presence_count = Presence.objects.filter(student=student).count()

    # Obter todos os gifts disponíveis
    gifts = Gift.objects.filter(min_presence__lte=presence_count, balance__gt=0)

    # Atribuir gifts ao aluno
    for gift in gifts:
        # Verificar se o aluno já recebeu este gift
        if not StudentGift.objects.filter(student=student, gift=gift).exists():
            # Criar a relação StudentGift
            StudentGift.objects.create(student=student, gift=gift)
            # Atualizar o saldo do gift
            update_gift_balance(gift)
            break  # Atribui apenas um gift por presença mínima atendida

def check_and_remove_gifts(student: Student):
    # Obter todos os gifts atribuídos ao aluno
    student_gifts = StudentGift.objects.filter(student=student)

    # Verifica quantas presenças o aluno tem
    presence_count = Presence.objects.filter(student=student).count()

    # Valida os gifts atribuídos
    for student_gift in student_gifts:
        gift = student_gift.gift
        # Se o aluno não atende mais ao critério de presença mínima, remove o gift
        if presence_count < gift.min_presence:
            student_gift.delete()
            # Atualiza o saldo do gift
            update_gift_balance(gift)

def check_and_remove_gifts_from_gift(gift: Gift):
    student_gifts = StudentGift.objects.filter(gift=gift)

    for student_gift in student_gifts:
        student = student_gift.student

        # Verifica quantas presenças o aluno tem
        presence_count = Presence.objects.filter(student=student).count()

        # Se o número de presenças for menor
        if presence_count < gift.min_presence:
            student_gift.delete()
            # Atualiza o saldo
            update_gift_balance(gift)