import random
import string
from uuid import UUID

from django.db import models
from django.http import Http404, JsonResponse
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from services.api.decorators import (
    admin_auth_required,
    firebase_auth_required,
    student_auth_required,
)
from services.presences.models import Presence

from .models import Student, StudentGift
from .serializers import (
    StudentGiftSerializer,
    StudentListSerializer,
    StudentSerializer,
)
from .utils import apply_student_gift_filters, generate_unique_code

# Create your views here.

def generate_unique_code(length=3):
    """Gera um código unico para registrar presenças de estudantes"""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        if not Student.objects.filter(code=code).exists():
            break
    return code

############################################################################################################
#                                         FIREBASE REQUIRED VIEWS
############################################################################################################
@extend_schema(
    summary="Login student",
    tags=["Students"],
)
@method_decorator(firebase_auth_required, name='dispatch')
class StudentLogin(APIView):

    def post(self, request, *args, **kwargs):
        """Sistema de login do estudante

        Este é um endpoint que funciona através da autenticação do firebase, não o use diretamente.
        Apenas o chame depois que estiver logado no firebase.
        """
        data = request.data

        required_fields = ['name', 'email']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return JsonResponse(
                {'error': f"Campos obrigatórios faltando: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = data.get('email')
        student = Student.objects.filter(email=email).first()

        if student:
            # Gera um novo token de acesso
            refresh = RefreshToken.for_user(student)
            access_token = refresh.access_token

            return Response({
                'id': student.id,
                'access': str(access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        unique_code = generate_unique_code()
        new_student = Student.objects.create(
            name=data.get('name'),
            email=email,
            code=unique_code,
            usp_number=data.get('usp_number'),
        )

        refresh = RefreshToken.for_user(new_student)
        access_token = refresh.access_token

        return Response({
            'id': new_student.id,
            'name': new_student.name,
            'email': new_student.email,
            'code': new_student.code,
            'usp_number': new_student.usp_number,
            'created_at': new_student.created_at,
            'updated_at': new_student.updated_at,
            'access': str(access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


############################################################################################################
#                                             STUDENT VIEWS
############################################################################################################
@extend_schema(
    tags=["Students"],
    summary="Index Student"
)
@student_auth_required
@api_view(['GET'])
def student_index(request):
    """Ponto de entrada para a área de estudantes"""
    return Response({"message": "Bem-vinde à área exclusiva de estudantes!"}, status=200)


@extend_schema(tags=["Students"], summary="Retrieve student")
@method_decorator(student_auth_required, name="dispatch")
class StudentRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    # Pega student_id da url e verifica contra id no banco
    lookup_url_kwarg = "student_id"
    lookup_field = "id"


@extend_schema(tags=["Students"], summary="Retrieve student's presences")
@method_decorator(student_auth_required, name='dispatch')
class RetrieveStudentPresencesView(generics.ListAPIView):
    """Retorna as presenças que o estudante possui"""
    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        return Presence.objects.filter(student_id=student_id).select_related('talk')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        presence_list = [
            {
              "talk_title": p.talk.title,
              "start_time": p.talk.start_time,
              "end_time": p.talk.end_time,
            }
            for p in queryset
        ]
        return Response(presence_list)

@extend_schema(tags=["Students"], summary="Retrieve student's gifts")
@method_decorator(student_auth_required, name='dispatch')
class ListRetrieveStudentGiftsView(generics.ListAPIView):
    """
    Lista todos os brindes associados ao usuário logado
    A lista é filtrada usando funcao utilitária apply_student_gift_filters
    """
    serializer_class = StudentGiftSerializer

    def get_queryset(self):
        student = self.request.user
        queryset = StudentGift.objects.filter(student=student.id)
        return apply_student_gift_filters(self, queryset)

############################################################################################################
#                                               ADMIN VIEWS
############################################################################################################
@extend_schema(tags=["Students"], summary="List students")
@method_decorator(admin_auth_required, name="dispatch")
class AdminListStudentsView(generics.ListAPIView):
    """Lista todos os estudantes"""

    queryset = Student.objects.all()
    serializer_class = StudentListSerializer


@extend_schema(tags=["Students"], summary="Retrieve student by name")
@method_decorator(admin_auth_required, name="dispatch")
class AdminListStudentsByNameView(generics.ListAPIView):
    """Retorna todos os estudantes que contenham em seus nomes `name`."""

    serializer_class = StudentListSerializer

    def get_queryset(self):
        name = self.kwargs.get("name")
        return Student.objects.filter(name__icontains=name)


@extend_schema(tags=["Students"], summary="Retrieve student")
@method_decorator(admin_auth_required, name='dispatch')
class AdminRetrieveStudentInfoView(generics.RetrieveAPIView):
    """Retorna as informações de um estudante"""
    def get(self, request, *args, **kwargs):
        student_document = self.kwargs.get('student_document')

        student = Student.objects.filter(
          models.Q(email=student_document) |
          models.Q(code=student_document.upper()) |
          models.Q(usp_number=student_document)
        ).first()

        if not student:
            return Response({'error': f"Estudante com documento {student_document} não encontrado."}, status=status.HTTP_400_BAD_REQUEST)

        in_person_presences_count = Presence.objects.filter(student=student).count()
        total_presences_count = Presence.objects.filter(student=student).count()
        presences_with_talk_title = (
            Presence.objects
            .select_related('talk')
            .filter(student=student)
            .annotate(talk_title=models.F('talk__title'))
            .values('talk_title')
        )

        return Response(
            {
                "id": student.id,
                "email": student.email,
                "name": student.name,
                "code": student.code,
                "created_at": student.created_at,
                "updated_at": student.updated_at,
                "in_person_presences_count": in_person_presences_count,
                "total_presences_count": total_presences_count,
                "presences": list(presences_with_talk_title),
            }
        )


@extend_schema(tags=["Students"], summary="Delete student")
@method_decorator(admin_auth_required, name='delete')
class AdminDestroyStudentView(generics.DestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'student_document'

    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)

        assert self.queryset is not None
        student = self.queryset.filter(
            models.Q(email=lookup_value) |
            models.Q(code=lookup_value) |
            models.Q(usp_number=lookup_value)
        ).first()

        if not student:
            raise Http404(f"Estudante com documento {lookup_value} não encontrado.")
        return student

    def delete(self, request, *args, **kwargs):
        """Apaga um estudante da base da dados.
        **Nota:**
        Isso não apaga o registro do estudante no firebase.
        """
        student = self.get_object()
        student.delete()
        return Response({'message': f'Estudante {student.name} removido com sucesso.'}, status=status.HTTP_200_OK)

@extend_schema(tags=["Students"], summary="Retrieve student's gifts")
@method_decorator(admin_auth_required, name='dispatch')
class AdminListRetrieveStudentGiftsByStudentView(generics.ListAPIView):
    """
    Lista os brindes associados a um student_id
    A lista é filtrada usando funcao utilitária apply_student_gift_filters
    """
    serializer_class = StudentGiftSerializer

    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        queryset = StudentGift.objects.filter(student_id=student_id)
        return apply_student_gift_filters(self, queryset)

@extend_schema(tags=["Students"], summary="Update student's gifts")
@method_decorator(admin_auth_required, name='dispatch')
class AdminUpdateStudentGiftView(generics.UpdateAPIView):
    """
    Atualiza o campo `received` dos brindes dos estudantes. Indicando que ele foi retirado, esse é o único campo permitido editar.
    """
    serializer_class = StudentGiftSerializer
    queryset = StudentGift.objects.all()

    @extend_schema(summary="Update student gift received status")
    @method_decorator(admin_auth_required, name='update')
    def update(self, request, *args, **kwargs):
        gift_id = kwargs.get('pk')

        print(gift_id)
        try:
            student_gift = StudentGift.objects.get(pk=gift_id)
        except StudentGift.DoesNotExist:
            return Response({'error': 'Student gift not found'}, status=status.HTTP_404_NOT_FOUND)

        if 'received' not in request.data:
            return Response({'error': 'Field "received" is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Only allow updating the received field
        student_gift.received = bool(request.data.get('received'))
        student_gift.save()

        serializer = self.get_serializer(student_gift)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Students"], summary="Retrieve student")
@method_decorator(admin_auth_required, name="dispatch")
class AdminRetrieveStudentById(generics.RetrieveAPIView):
    """Retorna um estudante pelo seu id."""

    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    lookup_url_kwarg = "student_id"
    lookup_field = "id"
