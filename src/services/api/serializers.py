from rest_framework import serializers

from .models import *
from .utils import *

from services.students.models import Student


class TokenSerializer(serializers.ModelSerializer):
    begin = serializers.DateTimeField(format=datetime_url_format, input_formats=[datetime_url_format])
    duration = serializers.IntegerField(required=False, default=5, help_text='Opcional (padrão=5)')  # Em minutos
    code = serializers.CharField(read_only=True)

    class Meta:
        model = Token
        fields = '__all__'

    def validate(self, data):
        if not Talk.objects.filter(id=data['talk'].id).exists():
            raise serializers.ValidationError(f"Palestra com id {data['talk'].id} não encontrada.")

        return data

    def create(self, validated_data):
        talk = validated_data['talk']
        begin = validated_data['begin']
        duration = validated_data['duration']
        code = generate_token_code()

        token = Token(talk=talk, begin=begin, duration=duration, code=code)
        token.save()
        return token

class OnlinePresenceSerializer(serializers.ModelSerializer):
    token_code = serializers.CharField(write_only=True)

    class Meta:
        model = Presence
        fields = ['token_code']



class AdminSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

class EmptySerializer(serializers.Serializer):
    pass
