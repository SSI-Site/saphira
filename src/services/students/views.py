from datetime import datetime as dt, timedelta
import string
import random
from zoneinfo import ZoneInfo

from django.db import models
from django.http import Http404, JsonResponse
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from services.api.decorators import admin_auth_required, firebase_auth_required, student_auth_required
from services.api.models import Presence, Token
from services.api.serializers import OnlinePresenceSerializer
from .serializers import StudentSerializer
from .models import Student

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
@method_decorator(firebase_auth_required, name='dispatch')
class StudentLogin(APIView):
    def post(self, request, *args, **kwargs):
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
@student_auth_required
@api_view(['GET'])
def student_index(request):
    return Response({"message": "Bem-vinde à área exclusiva de estudantes!"}, status=200)

@method_decorator(student_auth_required, name='dispatch')
class StudentRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get(self, request, *args, **kwargs):
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

    def put(self, request, *args, **kwargs):
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

@method_decorator(student_auth_required, name='dispatch')
class CreateStudentOnlinePresenceView(generics.CreateAPIView):
    serializer_class = OnlinePresenceSerializer
    queryset = Presence.objects.all()

    def post(self, request, *args, **kwargs):
        token_code = request.data.get('token_code')
        student_id = self.kwargs.get('student_id')

        if not token_code:
            return Response({'error': 'Token não informado.'}, status=status.HTTP_400_BAD_REQUEST)

        token = Token.objects.filter(code=token_code.upper()).first()

        if not token:
            return Response({'error': 'Token inválido.'}, status=status.HTTP_401_UNAUTHORIZED)

        duration = timedelta(minutes=token.duration)

        now = dt.now(ZoneInfo('America/Sao_Paulo')) # Horário de Brasília
        begin = token.begin
        end = begin + duration

        if not (begin <= now <= end):
            return Response({'error': 'Token expirado.'}, status=status.HTTP_401_UNAUTHORIZED)

        student = Student.objects.filter(id=student_id).first()

        if Presence.objects.filter(student=student, talk=token.talk).exists():
            return Response({'error': 'Presença já registrada nessa palestra.'}, status=status.HTTP_400_BAD_REQUEST)

        presence = Presence.objects.create(
            student=student,
            talk=token.talk,
        )

        return Response({
          'student': presence.student.id,
          'talk': presence.talk.id,
        }, status=status.HTTP_201_CREATED)

@method_decorator(student_auth_required, name='dispatch')
class RetrieveStudentPresencesView(generics.ListAPIView):
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

############################################################################################################
#                                               ADMIN VIEWS
############################################################################################################
@method_decorator(admin_auth_required, name='dispatch')
class AdminListStudentsView(generics.ListAPIView):
    queryset = Student.objects.all()

    def get(self, request, *args, **kwargs):
        students = self.get_queryset().values('id', 'name', 'code')
        return Response(list(students))

@method_decorator(admin_auth_required, name='dispatch')
class AdminListStudentsByNameView(generics.ListAPIView):
    queryset = Student.objects.all()

    def get(self, request, *args, **kwargs):
        name = self.kwargs.get('name')
        students = Student.objects.filter(name__icontains=name).values('id', 'name', 'code', 'email')
        return Response(list(students))

@method_decorator(admin_auth_required, name='dispatch')
class AdminRetrieveStudentInfoView(generics.RetrieveAPIView):
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

        return Response({
            'id': student.id,
            'name': student.name,
            'code': student.code,
            'in_person_presences_count': in_person_presences_count,
            'total_presences_count': total_presences_count,
            'presences': list(presences_with_talk_title)
        })

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
        student = self.get_object()
        student.delete()
        return Response({'message': f'Estudante {student.name} removido com sucesso.'}, status=status.HTTP_200_OK)
