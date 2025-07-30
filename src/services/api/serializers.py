from rest_framework import serializers

class AdminSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

class EmptySerializer(serializers.Serializer):
    pass
