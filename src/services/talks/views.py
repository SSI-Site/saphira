from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema
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
@extend_schema(tags=['Talks'], summary="List talks")
class ListRetrieveTalksView(generics.ListAPIView):
    """
    Lista todas as palestras
    Você pode filtrar a lista usando os seguintes parâmetros na URL:
    - `date`: Filtra por data específica. Ex: /talks/?date=2025-07-27T14:30
    - `start_date`: Filtra talks a partir de uma data. Ex: /talks/?start_date=2025-07-27T00:00
    - `end_date`: Filtra talks até uma data. Ex: /talks/?end_date=2025-07-30T23:59
    - `title`: Filtra por título da talk. Ex: /talks/?title=Python
    """
    serializer_class = TalkSerializer

    def get_queryset(self):
        queryset = Talk.objects.all()
        return apply_talk_filters(self, queryset)

############################################################################################################
#                                               ADMIN VIEWS
############################################################################################################

@extend_schema(tags=['Sponsors'], summary="List sponsors")
@method_decorator(admin_auth_required, name='dispatch')
class AdminListCreateSponsorView(generics.ListCreateAPIView):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer

    @extend_schema(tags=['Sponsors'], summary="Create sponsors")
    def create(self, request, *args, **kwargs):
        """Cria um patrocinador de palestras.

        São necessários os campos:
        - `name`: Nome do patrocinador
        - `url_link`: Link para a página do patrocinador
        - `sponsor_type`: Tipo de patrocinador (Sponsor, Partner)
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {"message": "Sponsor criado com sucesso.", "sponsor": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Talks'], summary="Retrieve sponsor")
@method_decorator(admin_auth_required, name='dispatch')
class AdminRetrieveUpdateDestroySponsorView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer

    @extend_schema(summary="Update sponsor")
    def update(self, request, *args, **kwargs):
        """Atualiza um patrocinador com base no id"""
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

    @extend_schema(summary="Deletes a sponsor")
    def delete(self, request, *args, **kwargs):
        """Remove um sponsor.

        **Nota:**
        Essa rota falha caso existam palestras associadas a esse patrocinador.
        Remova ou edite essas palestras.
        """
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

@extend_schema(tags=['Talks'], summary="List sponsor")
@method_decorator(admin_auth_required, name='dispatch')
class AdminListCreateTalksView(generics.ListCreateAPIView):
    queryset = Talk.objects.all()
    serializer_class = TalkSerializer

    @extend_schema(tags=['Talks'], summary="Create talk")
    def create(self, request, *args, **kwargs):
        """Cria um palestra
        É necessário definir os campos:
        - `title`: Título da palestra
        - `description`: Descrição da palestra
        - `start_time`: Horário de início da palestra
        - `end_time`: Horário de fim da palestra
        - `speakers`: Lista de IDs dos palestrantes
        """
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

@extend_schema(tags=['Talks'], summary="Retrieve talk")
@method_decorator(admin_auth_required, name='dispatch')
class AdminRetrieveUpdateDestroyTalkView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Talk.objects.all()
    serializer_class = TalkSerializer

    @extend_schema(tags=['Talks'], summary="Delete talk")
    def delete(self, request, *args, **kwargs):
        """Remover palestra"""
        talk = self.get_object()
        talk.delete()
        return Response({'message': 'Palestra removida com sucesso.'}, status=status.HTTP_200_OK)
