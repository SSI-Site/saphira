from rest_framework import serializers

from .models import *
from .utils import *


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'email', 'usp_number']

class TalkSerializer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(format=datetime_url_format, input_formats=[datetime_url_format])

    class Meta:
        model = Talk
        fields = '__all__'
        extra_kwargs = {
            'speaker': {'required': False, 'allow_blank': True, 'help_text': 'Opcional'},
            'description': {'required': False, 'allow_blank': True, 'help_text': 'Opcional'},
        }

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

class CreatePresenceSerializer(serializers.ModelSerializer):
    student_document = serializers.CharField(write_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    talk = serializers.PrimaryKeyRelatedField(queryset=Talk.objects.all())

    class Meta:
        model = Presence
        fields = ['student_document', 'talk', 'student']

    def create(self, validated_data):
        student_document = validated_data.pop('student_document')
        talk = validated_data.pop('talk')

        student = Student.objects.filter(
            models.Q(email=student_document) | 
            models.Q(code=student_document.upper()) | 
            models.Q(usp_number=student_document)
        ).first()

        if not student:
            raise serializers.ValidationError(f"Estudante com documento {student_document} não encontrado.")

        if Presence.objects.filter(student=student, talk=talk).exists():
            raise serializers.ValidationError(f'Presença já registrada para o estudante com documento {student_document} nesta palestra.')

        presence = Presence.objects.create(student=student, talk=talk, **validated_data)
        return presence

class AdminSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

class EmptySerializer(serializers.Serializer):
    pass
