from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.response import Response

from services.api.decorators import admin_auth_required
from services.speakers.models import Speaker
from .models import Talk
from .serializers import TalkSerializer

# Create your views here.

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
