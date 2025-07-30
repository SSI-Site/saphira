from rest_framework import serializers
from .models import Gift

class GiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gift
        fields = ['id', 'name', 'description', 'min_presence', 'total_amount', 'balance']

    def create(self, validated_data):
        gift = Gift.objects.create(
            id=validated_data.get('id', None),
            name=validated_data['name'],
            description=validated_data.get('description', None),
            min_presence=validated_data.get('min_presence', 1),
            total_amount=validated_data.get('total_amount', 0),
            balance=validated_data.get('total_amount', 0)  # Inicialmente, o saldo é igual ao total
        )
        return gift

class GiftPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gift
        fields = ['id', 'name', 'description', 'min_presence']


class GiftPrivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gift
        fields = ['id', 'name', 'description', 'min_presence', 'total_amount', 'balance']
