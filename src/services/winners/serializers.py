from rest_framework import serializers

from services.students.models import Student
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
