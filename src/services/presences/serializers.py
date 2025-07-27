
from django.db import models
from rest_framework import serializers

from services.presences.models import Presence
from services.students.models import Student
from services.talks.models import Talk


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
