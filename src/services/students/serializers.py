from rest_framework import serializers
from .models import Student, StudentGift
from ..gifts.serializers import GiftPublicSerializer

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'email', 'usp_number']

class StudentGiftSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    gift = GiftPublicSerializer(read_only=True)

    class Meta:
        model = StudentGift
        fields = ['id', 'student', 'gift', 'received', 'created_at', 'updated_at']