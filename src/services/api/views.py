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
from uuid import UUID

from services.gifts.utils import check_and_remove_gifts, check_and_assign_gifts


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

class RetrieveSpeakerByNameView(generics.ListAPIView):
    def get_queryset(self):
        name = self.kwargs.get('name')
        return Speaker.objects.filter(name__icontains=name)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        speakers = [
            {
                'id': speaker.id,
                'name': speaker.name,
                'description': speaker.description,
                'social_media': speaker.social_media,
                'pronouns': speaker.pronouns
            }
            for speaker in queryset
        ]
        return Response(speakers)

class RetrieveSpeakersView(generics.RetrieveAPIView):
    queryset = Speaker.objects.all()

    def get(self, request, *args, **kwargs):
        speakers = self.get_queryset().values('id', 'name', 'description', 'social_media', 'pronouns', 'role')
        return Response(list(speakers))

############################################################################################################
#                                               ADMIN VIEWS
############################################################################################################
@api_view(['GET'])
@admin_auth_required
def admin_index(request):
    return Response({"message": "Credenciais incorretas!! Brincadeirinha...o login deu bom =)"}, status=200)

@method_decorator(admin_auth_required, name='dispatch')
class AdminCreateSpeakerView(generics.CreateAPIView):
    serializer_class = SpeakerSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {"message": "Palestrante criado com sucesso.", "speaker": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(admin_auth_required, name='delete')
class AdminUpdateDestroySpeakerView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'speaker_id'

    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)
        speaker = Speaker.objects.filter(id=lookup_value).first()

        if not speaker:
            raise Http404(f"Palestrante com id {lookup_value} não encontrado.")
        return speaker

    def put(self, request, *args, **kwargs):
        speaker = self.get_object()
        allowed_fields = [
            'name',
            'description',
            'social_media',
            'pronouns'
        ]

        for field in allowed_fields:
            if field in request.data:
                setattr(speaker, field, request.data[field])

        speaker.save()

        return Response({
            'id': speaker.id,
            'name': speaker.name,
            'description': speaker.description,
            'social_media': speaker.social_media,
            'pronouns': speaker.pronouns,
        })

    def delete(self, request, *args, **kwargs):
        speaker = self.get_object()
        speaker.delete()
        return Response({'message': f'Palestrante {speaker.name} removido com sucesso.'}, status=status.HTTP_200_OK)

@method_decorator(admin_auth_required, name='dispatch')
class AdminListCreateTalksView(generics.ListCreateAPIView):
    queryset = Talk.objects.all()
    serializer_class = TalkSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        speaker_id = request.data['speaker']
        speaker = Speaker.objects.filter(id=speaker_id).first()

        if not speaker:
            return Response({'error': f"Palestrante com id {speaker_id} não encontrado(a)."}, status=status.HTTP_400_BAD_REQUEST)

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

            # Atualiza o saldo do Gift se o aluno tiver direito a algum
            student = presence.student
            check_and_assign_gifts(student)

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

        # Verifica se o aluno ainda tem direito a algum Gift
        check_and_remove_gifts(presence.student)

        return Response({'message': 'Presença removida com sucesso.'}, status=status.HTTP_200_OK)

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
            'id': student.id,
            'name': student.name,
            'email': student.email,
            'code': student.code,
            'usp_number': student.usp_number,
        })

@method_decorator(admin_auth_required, name='dispatch')
class AdminListWinnerView(generics.ListAPIView):
    queryset = DrawWinner.objects.all()

    def get(self, request, *args, **kwargs):
        draw_winners = self.get_queryset().values('id', 'student', 'talk')

        return Response(list(draw_winners))

@method_decorator(admin_auth_required, name='dispatch')
class AdminDestroyWinnerView(generics.DestroyAPIView):
    lookup_field = 'student_id'

    def get_queryset(self):
        return DrawWinner.objects.all()

    def get_object(self):
        object = self.get_queryset().filter(student_id=self.kwargs.get(self.lookup_field)).first()
        if not object:
            raise Http404('Vencedor não encontrado.')
        return object

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()

        return Response({'message': 'Vencedor removido com sucesso.'}, status=status.HTTP_200_OK)
