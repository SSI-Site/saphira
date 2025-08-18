import string
import random

from django.db import models
from django.http import Http404, JsonResponse
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from services.api.decorators import admin_auth_required, firebase_auth_required, student_auth_required
from services.presences.models import Presence
from .serializers import StudentSerializer, StudentGiftSerializer
from .models import Student, StudentGift
from .utils import apply_student_gift_filters


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

@extend_schema(
    tags=["Students"],
    summary="Retrieve student"
)
@method_decorator(student_auth_required, name='dispatch')
class StudentRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get(self, request, *args, **kwargs):
        """Retorna um estudante com base no `id`"""
        student_id = kwargs.get('student_id')

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=404)

        return Response({
            'id': student.id,
            'name': student.name,
            'email': student.email,
            'code': student.code,
            'usp_number': student.usp_number,
        })

    @extend_schema(summary="Update student")
    def put(self, request, *args, **kwargs):
        """Atualiza o estudante.

        É possível atualizar os seguintes campos: `usp_number`
        """
        student_id = kwargs.get('student_id')

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=404)

        allowed_fields = ['usp_number']

        for field in allowed_fields:
            if field in request.data:
                setattr(student, field, request.data[field])

        student.save()

        return Response({
            'id': student.id,
            'name': student.name,
            'email': student.email,
            'code': student.code,
            'usp_number': student.usp_number,
        })

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
        queryset = StudentGift.objects.filter(student=student)
        return apply_student_gift_filters(self, queryset)

############################################################################################################
#                                               ADMIN VIEWS
############################################################################################################
@extend_schema(tags=["Students"], summary="List students")
@method_decorator(admin_auth_required, name='dispatch')
class AdminListStudentsView(generics.ListAPIView):
    """Lista todos os estudantes"""
    queryset = Student.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().values('id', 'email', 'name', 'code')
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(list(queryset))

@extend_schema(tags=["Students"], summary="Retrieve student by name")
@method_decorator(admin_auth_required, name='dispatch')
class AdminListStudentsByNameView(generics.ListAPIView):
    """Retorna todos os estudantes que contenham em seus nomes `name`."""
    queryset = Student.objects.all()

    def list(self, request, *args, **kwargs):
        name = self.kwargs.get('name')
        queryset = Student.objects.filter(name__icontains=name).values('id', 'name', 'code', 'email')
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(list(queryset))

@extend_schema(tags=["Students"], summary="Retrieve student")
@method_decorator(admin_auth_required, name='dispatch')
class AdminRetrieveStudentInfoView(generics.RetrieveAPIView):
    """Retorna as informações de um estudante"""
    def get(self, request, *args, **kwargs):
        student_document = self.kwargs.get('student_document')

        student = Student.objects.filter(
          models.Q(id=student_document) |
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

        return Response({
            'id': student.id,
            'email': student.email,
            'name': student.name,
            'code': student.code,
            'in_person_presences_count': in_person_presences_count,
            'total_presences_count': total_presences_count,
            'presences': list(presences_with_talk_title)
        })

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
