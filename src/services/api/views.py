
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .decorators import admin_auth_required
from .serializers import (
    AdminSerializer,
    EmptySerializer
)

from drf_spectacular.utils import extend_schema

############################################################################################################
#                                             PUBLIC VIEWS
############################################################################################################
@extend_schema(
    tags=['Public'],
    summary="Ponto de entrada",
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
@api_view(['GET'])
def index(request):
    """Ponto de entrada para o Saphira. Seja bem-vindo. Se essa endpoint não estiver funcionando o Saphira está fora do ar."""
    return Response({"message": "Bem-vinde à API Saphira!"}, status=status.HTTP_200_OK)

@extend_schema(
    tags=['Public'],
    summary="Adquirir token CSRF",
    responses={200: {"type": "object", "properties": {"csrfToken": {"type": "string"}}}}
)
@api_view(['GET'])
def csrf(request):
    """Rota apenas para retornar o token CSRF para frontend de cross-site origin. Deve ser chamada antes de qualquer outra requisição do fronted."""
    return JsonResponse({
        "csrfToken": get_token(request)
    })

@extend_schema(
    tags=['Admin'],
    summary="Admin login",
    methods=["POST"],
    responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}}
)
class AdminLoginView(APIView):
    serializer_class = AdminSerializer

    @extend_schema(summary="Admin auth")
    def post(self, request, *args, **kwargs):
        """Autenticação do Administrador"""
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

            return Response({'detail': 'Logado como admin...utilize seus poderes com moderação ;)'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Você não é da CO-SSI...'}, status=status.HTTP_401_UNAUTHORIZED)

@extend_schema(
    tags=["Admin"],
    summary="Admin Logout",
    methods=["POST"],
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
class AdminLogoutView(APIView):
    serializer_class = EmptySerializer

    # Usado pelo drf para mostrar na tela se o admin esta logado
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'message': 'Você não está logado como admin.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'message': 'Você está logado como admin.'}, status=status.HTTP_200_OK)

    @extend_schema(summary="Admin logout")
    def post(self, request):
        """Endpoint para deslogar da conta de adminstrador"""
        if not request.user.is_authenticated:
            return Response({'message': 'Você não está logado como admin.'}, status=status.HTTP_401_UNAUTHORIZED)
        logout(request)
        response = Response({'message': 'Parabéns, agora você não é mais admin :('}, status=status.HTTP_200_OK)
        response.delete_cookie('sessionid')
        return response

############################################################################################################
#                                               ADMIN VIEWS
############################################################################################################
@extend_schema(
    tags=["Admin"],
    summary="Admin index",
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
@api_view(['GET'])
@admin_auth_required
def admin_index(request):
    """Ponto de entrada para página de admin"""
    return Response({"message": "Credenciais incorretas!! Brincadeirinha...o login deu bom =)"}, status=200)
