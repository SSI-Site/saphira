from rest_framework import serializers

from services.students.models import Student
from services.students.serializers import StudentSerializer
from services.talks.serializers import TalkSerializer
from .models import DrawWinner


class DrawWinnerSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    talk = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = DrawWinner
        fields = ['id', 'talk', 'student']

    def create(self, validated_data):
        draw_winner = DrawWinner.objects.create(**validated_data)
        return draw_winner

    def to_representation(self, instance):
        """Devolve os dados do estudante e da palestra, e não apenas os seus ids.

        A entrada continua sendo feita por id (`student` e `talk`), apenas a saída muda.
        """
        student = StudentSerializer(instance.student).data
        talk = TalkSerializer(instance.talk).data

        return {
            'id': instance.id,
            'code': student['code'],
            'name': student['name'],
            'email': student['email'],
            'talkTitle': talk['title'],
        }
