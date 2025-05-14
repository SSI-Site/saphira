from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.db.models import F
from django.http import Http404, JsonResponse
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .decorators import *
from .models import *
from .serializers import *
from .utils import *


############################################################################################################
#                                             PUBLIC VIEWS
############################################################################################################
@api_view(['GET'])
def index(request):
    return Response({"message": "Bem-vinde à API Saphira!"}, status=status.HTTP_200_OK)

class AdminLoginView(APIView):
    serializer_class = AdminSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

            return Response({'detail': 'Logado como admin...utilize seus poderes com moderação ;)'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Você não é da CO-SSI...'}, status=status.HTTP_401_UNAUTHORIZED)

class AdminLogoutView(APIView):
    serializer_class = EmptySerializer

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'message': 'Você não está logado como admin.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'message': 'Você está logado como admin.'}, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'message': 'Você não está logado como admin.'}, status=status.HTTP_401_UNAUTHORIZED)
        logout(request)
        response = Response({'message': 'Parabéns, agora você não é mais admin :('}, status=status.HTTP_200_OK)
        response.delete_cookie('sessionid')
        return response


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
              "date_time": p.talk.date_time,
            }
            for p in queryset
        ]
        return Response(presence_list)


############################################################################################################
#                                               ADMIN VIEWS
############################################################################################################
@api_view(['GET'])
@admin_auth_required
def admin_index(request):
    return Response({"message": "Credenciais incorretas!! Brincadeirinha...o login deu bom =)"}, status=200)

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
            .annotate(talk_title=F('talk__title'))
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

@method_decorator(admin_auth_required, name='dispatch')
class AdminListCreateTalksView(generics.ListCreateAPIView):
    queryset = Talk.objects.all()
    serializer_class = TalkSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.perform_create(serializer)

            return Response(
                {"message": "Palestra criada com sucesso.", "talk": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(admin_auth_required, name='dispatch')
class AdminRetrieveUpdateDestroyTalkView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Talk.objects.all()
    serializer_class = TalkSerializer

    def delete(self, request, *args, **kwargs):
        talk = self.get_object()
        talk.delete()
        return Response({'message': 'Palestra removida com sucesso.'}, status=status.HTTP_200_OK)

@method_decorator(admin_auth_required, name='dispatch')
class AdminListCreateTokensView(generics.ListCreateAPIView):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.perform_create(serializer)

            return Response(
                {"message": "Token criado com sucesso.", "token": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(admin_auth_required, name='dispatch')
class AdminListCreatePresenceView(generics.ListCreateAPIView):
    queryset = Presence.objects.all()
    serializer_class = CreatePresenceSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            presence = serializer.save()
            return Response(self.get_serializer(presence).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(admin_auth_required, name='dispatch')
class AdminDestroyPresenceView(generics.DestroyAPIView):
    queryset = Presence.objects.all()

    def get_object(self):
        student_document = self.kwargs.get('student_document')
        talk_id = self.kwargs.get('talk_id')

        student = Student.objects.filter(
            models.Q(email=student_document) |
            models.Q(code=student_document.upper()) |
            models.Q(usp_number=student_document)
        ).first()

        if not student:
            raise Http404(f"Estudante com documento {student_document} não encontrado.")

        if not Talk.objects.filter(id=talk_id).exists():
            raise Http404(f"Palestra com id {talk_id} não encontrada.")

        presence = Presence.objects.filter(student=student, talk_id=talk_id).first()

        if not presence:
            raise Http404('Presença não registrada para o estudante nesta palestra.')

        return presence, None

    def delete(self, request, *args, **kwargs):
        presence, error = self.get_object()

        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        presence.delete()
        return Response({'message': 'Presença removida com sucesso.'}, status=status.HTTP_200_OK)

@method_decorator(admin_auth_required, name='dispatch')
class AdminInPersonDrawOnTalkView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        talk_id = self.kwargs.get('talk_id')

        talk = Talk.objects.filter(id=talk_id).first()

        if not talk:
            return Response({'error': f"Palestra com id {talk_id} não encontrada."}, status=status.HTTP_400_BAD_REQUEST)

        in_person_presences = Presence.objects.filter(talk=talk_id)

        if not in_person_presences.exists():
            return Response({'error': 'Nenhum estudante está presente em sala.'}, status=status.HTTP_400_BAD_REQUEST)

        random_presence = in_person_presences.order_by('?').first()
        student = random_presence.student

        return Response({
            'student_name': student.name
        })

@method_decorator(admin_auth_required, name='dispatch')
class AdminDrawOnTalkView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        talk_id = self.kwargs.get('talk_id')

        talk = Talk.objects.filter(id=talk_id).first()

        if not talk:
            return Response({'error': f"Palestra com id {talk_id} não encontrada."}, status=status.HTTP_400_BAD_REQUEST)

        presences = Presence.objects.filter(talk=talk_id)

        if not presences.exists():
            return Response({'error': 'Nenhum estudante presente nesta palestra.'}, status=status.HTTP_400_BAD_REQUEST)

        random_presence = presences.order_by('?').first()
        assert random_presence
        student = random_presence.student

        return Response({
            'student_name': student.name
        })
