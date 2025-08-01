from django.http import Http404
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Speaker
from .serializers import SpeakerSerializer
from ..api.decorators import admin_auth_required

############################################################################################################
#                                             PUBLIC VIEWS
############################################################################################################

@extend_schema(
    tags=["Speakers"],
    summary="Retrieve speakers"
)
class RetrieveSpeakerByNameView(generics.ListAPIView):
    """Retorna um palestrante a partir do seu nome."""
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
                'linkedin_link': speaker.linkedin_link,
                'instagram_link': speaker.instagram_link,
                'pronouns': speaker.pronouns
            }
            for speaker in queryset
        ]
        return Response(speakers)

@extend_schema(
    tags=["Speakers"],
    summary="List speakers"
)
class RetrieveSpeakersView(generics.RetrieveAPIView):
    """Retorna uma lista de todos os palestrantes"""
    queryset = Speaker.objects.all()

    def get(self, request, *args, **kwargs):
        speakers = self.get_queryset().values('id', 'name', 'description', 'linkedin_link', 'instagram_link', 'pronouns', 'role')
        return Response(list(speakers))

############################################################################################################
#                                               ADMIN VIEWS
############################################################################################################

@extend_schema(
    tags=["Speakers"],
    summary="Create Speakers"
)
@method_decorator(admin_auth_required, name='dispatch')
class AdminCreateSpeakerView(generics.CreateAPIView):
    """Cria um novo palestrante.

    Campos necessários:
    - `name`: nome do palestrante
    - `description`: descrição pessoal do palestrante
    - `linkedin_link`: link para o linkedin, no formato https://rede-social.com
    - `instagram_link`: link para o instagram, no formato https://rede-social.com
    - `pronouns`: pronomes do palestrante no formato pro/nome
    - `role`: cargo do palestrante, ex: (técnico de futebol, etc.)
    """
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

@extend_schema(
    summary="Get speaker by id",
    tags=["Speakers"]
)
@method_decorator(admin_auth_required, name='delete')
class AdminUpdateDestroySpeakerView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'speaker_id'

    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)
        speaker = Speaker.objects.filter(id=lookup_value).first()

        if not speaker:
            raise Http404(f"Palestrante com id {lookup_value} não encontrado.")
        return speaker

    @extend_schema(summary="Update speaker")
    def put(self, request, *args, **kwargs):
        """Atualiza palestrante.

        É possível atualizar os campos: `name`, `description`, 'linkedin_link', 'instagram_link', 'pronouns'
        e 'role'
    ]
        """
        speaker = self.get_object()
        allowed_fields = [
            'name',
            'description',
            'linkedin_link',
            'instagram_link',
            'pronouns',
            'role'
        ]

        for field in allowed_fields:
            if field in request.data:
                setattr(speaker, field, request.data[field])

        speaker.save()

        return Response({
            'id': speaker.id,
            'name': speaker.name,
            'description': speaker.description,
            'instagram_link': speaker.instagram_link,
            'linkedin_link': speaker.linkedin_link,
            'pronouns': speaker.pronouns,
        })

    @extend_schema(summary="Delete speaker")
    def delete(self, request, *args, **kwargs):
        """Remove um palestrante com base no id"""
        speaker = self.get_object()
        speaker.delete()
        return Response({'message': f'Palestrante {speaker.name} removido com sucesso.'}, status=status.HTTP_200_OK)
