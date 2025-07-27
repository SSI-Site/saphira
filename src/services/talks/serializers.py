from rest_framework import serializers

from services.api.utils import datetime_url_format
from .models import Talk

class TalkSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format=datetime_url_format, input_formats=[datetime_url_format])
    end_time = serializers.DateTimeField(format=datetime_url_format, input_formats=[datetime_url_format])

    class Meta:
        model = Talk
        fields = '__all__'
        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True, 'help_text': 'Opcional'},
        }
