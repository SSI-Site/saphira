from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.response import Response

from services.api.decorators import admin_auth_required
from services.api.serializers import EmptySerializer
from services.gifts.utils import check_and_assign_gifts, check_and_remove_gifts
from django.db import models
from services.presences.models import Presence
from services.presences.serializers import CreatePresenceSerializer
from services.students.models import Student
from services.talks.models import Talk

from drf_spectacular.utils import extend_schema
# Create your views here.

@extend_schema(
    tags=["Presences"],
    summary="List presences")
@method_decorator(admin_auth_required, name='dispatch')
class AdminListCreatePresenceView(generics.ListCreateAPIView):
    """Listagem de presenças"""
    queryset = Presence.objects.all()
    serializer_class = CreatePresenceSerializer

    @extend_schema(
        tags=["Presences"],
        summary="Create presence")
    def post(self, request, *args, **kwargs):
        """Registrar novas presenças

        É necessário o `id` do estudante e o `id` da palestra
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            presence = serializer.save()

            # Atualiza o saldo do Gift se o aluno tiver direito a algum
            student = presence.student
            check_and_assign_gifts(student)

            return Response(self.get_serializer(presence).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=["Presences"],
    summary="Remove presence")
@method_decorator(admin_auth_required, name='dispatch')
class AdminDestroyPresenceView(generics.DestroyAPIView):
    """Remoção de presenças

    Para remover uma presença é preciso do id da palestra, e o documento do estudante.
    O documento pode ser o _email_, _código_ ou _número usp_.
    """

    serializer_class = EmptySerializer
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
