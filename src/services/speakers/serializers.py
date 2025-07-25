from rest_framework import serializers

from services.speakers.models import Speaker

class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ['id', 'name', 'description', 'social_media', 'pronouns', 'role']

    def create(self, validated_data):
        speaker = Speaker.objects.create(**validated_data)
        return speaker