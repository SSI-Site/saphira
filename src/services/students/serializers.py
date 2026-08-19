from rest_framework import serializers

from ..gifts.serializers import GiftPublicSerializer
from .models import Student, StudentGift


class StudentLoginSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()


class StudentListSerializer(serializers.ModelSerializer):
    class Meta:
        model: type[Student] = Student
        fields: list[str] = [
            "id",
            "name",
            "email",
            "code",
            "created_at",
            "updated_at",
        ]


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'email', 'code', 'usp_number', 'created_at', 'updated_at']
        read_only_fields = ['code', 'created_at', 'updated_at']  # gerado pelo sistema, nunca enviado pelo cliente

class StudentGiftSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    gift = GiftPublicSerializer(read_only=True)

    class Meta:
        model = StudentGift
        fields = ['id', 'student', 'gift', 'received', 'created_at', 'updated_at']
