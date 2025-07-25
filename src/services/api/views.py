from datetime import datetime as dt, timedelta
from zoneinfo import ZoneInfo

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .decorators import *
from .serializers import *
from .utils import *

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

############################################################################################################
#                                               ADMIN VIEWS
############################################################################################################
@api_view(['GET'])
@admin_auth_required
def admin_index(request):
    return Response({"message": "Credenciais incorretas!! Brincadeirinha...o login deu bom =)"}, status=200)

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
