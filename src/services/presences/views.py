from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.response import Response

from services.api.decorators import admin_auth_required
from services.gifts.utils import check_and_assign_gifts, check_and_remove_gifts
from django.db import models
from services.presences.models import Presence
from services.presences.serializers import CreatePresenceSerializer
from services.students.models import Student
from services.talks.models import Talk

# Create your views here.
@method_decorator(admin_auth_required, name='dispatch')
class AdminListCreatePresenceView(generics.ListCreateAPIView):
    """Registro e recuperação de presenças"""
    queryset = Presence.objects.all()
    serializer_class = CreatePresenceSerializer

    def post(self, request, *args, **kwargs):
        """Registrar novas presenças"""
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
    """Remoção de presenças"""
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
