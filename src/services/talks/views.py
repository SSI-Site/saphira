from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.response import Response

from services.api.decorators import admin_auth_required
from services.speakers.models import Speaker

from .utils import apply_talk_filters
from .models import Talk, Sponsor
from .serializers import TalkSerializer, SponsorSerializer



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
class AdminListCreateSponsorView(generics.ListCreateAPIView):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {"message": "Sponsor criado com sucesso.", "sponsor": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(admin_auth_required, name='dispatch')
class AdminRetrieveUpdateDestroySponsorView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(
                {"message": "Sponsor atualizado com sucesso.", "sponsor": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        sponsor = self.get_object()

        if sponsor.talks.exists():
            return Response(
                {"error": "Este sponsor está associado a uma ou mais palestras e não pode ser removido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        sponsor.delete()
        return Response(
            {"message": "Sponsor removido com sucesso."},
            status=status.HTTP_200_OK
        )

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
