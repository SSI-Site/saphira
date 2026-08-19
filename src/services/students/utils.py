import random
import string

from services.students.models import Student


def apply_student_gift_filters(self, queryset):
    """
    Você pode filtrar a lista usando os seguintes parâmetros na URL:
    - `received`: Filtra por status de recebimento. Ex: /student/gifts/?received=true
    - `gift_name`: Filtra por nome do gift. Ex: /student/gifts/?gift_name=Can
    """
    received = self.request.query_params.get("received")
    if received is not None:
        received_bool = received.lower() == "true"
        queryset = queryset.filter(received=received_bool)

    gift_name = self.request.query_params.get("gift_name")
    if gift_name:
        queryset = queryset.filter(gift__name__icontains=gift_name)

    return queryset


def generate_unique_code(length: int = 3):
    """Gera um código unico para registrar presenças de estudantes"""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = "".join(random.choices(characters, k=length))
        if not Student.objects.filter(code=code).exists():
            break
    return code
