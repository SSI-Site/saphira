import random
import string
from uuid import UUID
from api.models import Gift, Student, StudentGift

datetime_url_format = "%Y-%m-%dT%H:%M"

def generate_unique_code(length=3):
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        if not Student.objects.filter(code=code).exists():
            break
    return code

def generate_token_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))

def update_gift_balance (gift):
    # Obtém o número de alunos que possuem esse Gift
    students_count = StudentGift.objects.filter(gift=gift).count()
    # Atualiza o saldo do Gift
    gift.balance = students_count
    gift.save()

class UUIDConverter:
    regex = '[0-9a-fA-F-]+'  # Regex para UUID com hífens

    def to_python(self, value):
        return UUID(value)

    def to_url(self, value):
        return str(value)