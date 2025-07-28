from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.response import Response

from services.api.decorators import admin_auth_required
from services.speakers.models import Speaker
from .models import Talk
from .serializers import TalkSerializer
from .utils import apply_talk_filters


############################################################################################################
#                                             PUBLIC VIEWS
############################################################################################################

class ListRetrieveTalksView(generics.ListAPIView):
    """
    Lista todas as palestras
    A lista é filtrada usando funcao utilitária apply_talk_filters
    """
    serializer_class = TalkSerializer

    def get_queryset(self):
        queryset = Talk.objects.all()
        return apply_talk_filters(self, queryset)

############################################################################################################
#                                               ADMIN VIEWS
############################################################################################################

@method_decorator(admin_auth_required, name='dispatch')
class AdminListCreateTalksView(generics.ListCreateAPIView):
    queryset = Talk.objects.all()
    serializer_class = TalkSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        speaker_ids = request.data.get('speakers', [])
        if not speaker_ids:
            return Response({'error': "Pelo menos um palestrante deve ser especificado."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar se todos os speakers existem
        existing_speakers = Speaker.objects.filter(id__in=speaker_ids)
        if len(existing_speakers) != len(speaker_ids):
            missing_ids = set(speaker_ids) - set(existing_speakers.values_list('id', flat=True))
            return Response({'error': f"Palestrantes com ids {list(missing_ids)} não encontrados."}, status=status.HTTP_400_BAD_REQUEST)

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
