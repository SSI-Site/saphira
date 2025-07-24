from django.http import Http404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Speaker
from .serializers import SpeakerSerializer
from ..api.decorators import admin_auth_required

############################################################################################################
#                                             PUBLIC VIEWS
############################################################################################################

class RetrieveSpeakerByNameView(generics.ListAPIView):
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
                'social_media': speaker.social_media,
                'pronouns': speaker.pronouns
            }
            for speaker in queryset
        ]
        return Response(speakers)

class RetrieveSpeakersView(generics.RetrieveAPIView):
    queryset = Speaker.objects.all()

    def get(self, request, *args, **kwargs):
        speakers = self.get_queryset().values('id', 'name', 'description', 'social_media', 'pronouns', 'role')
        return Response(list(speakers))

############################################################################################################
#                                               ADMIN VIEWS
############################################################################################################

@method_decorator(admin_auth_required, name='dispatch')
class AdminCreateSpeakerView(generics.CreateAPIView):
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

@method_decorator(admin_auth_required, name='delete')
class AdminUpdateDestroySpeakerView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'speaker_id'

    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)
        speaker = Speaker.objects.filter(id=lookup_value).first()

        if not speaker:
            raise Http404(f"Palestrante com id {lookup_value} não encontrado.")
        return speaker

    def put(self, request, *args, **kwargs):
        speaker = self.get_object()
        allowed_fields = [
            'name',
            'description',
            'social_media',
            'pronouns'
        ]

        for field in allowed_fields:
            if field in request.data:
                setattr(speaker, field, request.data[field])

        speaker.save()

        return Response({
            'id': speaker.id,
            'name': speaker.name,
            'description': speaker.description,
            'social_media': speaker.social_media,
            'pronouns': speaker.pronouns,
        })

    def delete(self, request, *args, **kwargs):
        speaker = self.get_object()
        speaker.delete()
        return Response({'message': f'Palestrante {speaker.name} removido com sucesso.'}, status=status.HTTP_200_OK)
