from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.response import Response

from services.api.decorators import admin_auth_required
from services.api.models import Presence, Talk
from services.students.models import Student
from services.winners.models import DrawWinner
from services.winners.serializers import DrawWinnerSerializer

# Create your views here.

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
    serializer_class = DrawWinnerSerializer
    lookup_url_kwarg = 'winner_id'

    def get_queryset(self):
        return DrawWinner.objects.all()

    def get_object(self):
        obj = self.get_queryset().filter(id=self.kwargs.get(self.lookup_url_kwarg)).first()
        if not obj:
            raise Http404('Vencedor não encontrado.')
        return obj

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()

        return Response({'message': 'Vencedor removido com sucesso.'}, status=status.HTTP_200_OK)

@method_decorator(admin_auth_required, name='dispatch')
class AdminListCreateWinner(generics.ListCreateAPIView):
    serializer_class = DrawWinnerSerializer
    queryset = DrawWinner.objects.all()

    def get(self, request, *args, **kwargs):
        talk_id = self.kwargs.get('talk_id')

        talk = Talk.objects.filter(id=talk_id).first()
        if not talk:
            return Response({'error': f"Palestra com id {talk_id} não encontrada."}, status=status.HTTP_400_BAD_REQUEST)

        draw_winners = DrawWinner.objects.filter(talk=talk_id).values('id', 'talk', 'student')
        return Response(list(draw_winners))

    def post(self, request, *args, **kwargs):
        talk_id = self.kwargs.get('talk_id')

        talk = Talk.objects.filter(id=talk_id).first()
        if not talk:
            return Response({'error': f"Palestra com id {talk_id} não encontrada."}, status=status.HTTP_400_BAD_REQUEST)

        student_id = request.data.get('student')
        student = Student.objects.filter(id=student_id).first()
        if not student:
            return Response({'error': f"Alune com id {student_id} não encontrade."}, status=status.HTTP_400_BAD_REQUEST)

        if not Presence.objects.filter(student=student_id, talk=talk_id).exists():
            return Response({'error': 'Alune com presença não registrada nessa palestra.'}, status=status.HTTP_400_BAD_REQUEST)

        if DrawWinner.objects.filter(student=student, talk=talk_id).exists():
            return Response({'error': 'Alune já recebeu brinde nessa palestra.'}, status=status.HTTP_400_BAD_REQUEST)

        draw_winner = DrawWinner.objects.create(talk=talk, student=student)
        return Response({
            'id': draw_winner.id,
            'student': draw_winner.student.id,
            'talk': draw_winner.talk.id,
        }, status=status.HTTP_201_CREATED)

@method_decorator(admin_auth_required, name='dispatch')
class AdminRetrieveWinnerByStudentView(generics.RetrieveAPIView):
    serializer_class = DrawWinnerSerializer
    lookup_url_kwarg = 'student_id'

    def get_queryset(self):
        return DrawWinner.objects.all()

    def get(self, request, *args, **kwargs):
        student_id = self.kwargs.get(self.lookup_url_kwarg)
        draw_winners = self.get_queryset().filter(student_id=student_id).values('id', 'talk', 'student')

        if not draw_winners:
            return Response({'error': f"Não há brindes registrados para alune de id {student_id}."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(list(draw_winners))

@method_decorator(admin_auth_required, name='dispatch')
class AdminRetrieveWinnerByTalkView(generics.RetrieveAPIView):
    serializer_class = DrawWinnerSerializer
    lookup_url_kwarg = 'talk_id'

    def get_queryset(self):
        return DrawWinner.objects.all()

    def get(self, request, *args, **kwargs):
        talk_id = self.kwargs.get(self.lookup_url_kwarg)
        draw_winners = self.get_queryset().filter(talk_id=talk_id).values('id', 'student', 'talk')

        if not draw_winners:
            return Response({'error': f"Não há sorteados registrados para palestra de id {talk_id}."}, status=status.HTTP_404_NOT_FOUND)

        return Response(list(draw_winners))
