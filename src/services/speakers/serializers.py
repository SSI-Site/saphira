from rest_framework import serializers

from services.speakers.models import Speaker

class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ['id', 'name', 'description', 'linkedin_link', 'instagram_link', 'pronouns', 'role']

    def create(self, validated_data):
        speaker = Speaker.objects.create(**validated_data)
        return speaker
