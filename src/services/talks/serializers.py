from rest_framework import serializers

from services.api.utils import datetime_url_format
from services.speakers.models import Speaker
from .models import Talk, TalkActivityType

class TalkSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format=datetime_url_format, input_formats=[datetime_url_format])
    end_time = serializers.DateTimeField(format=datetime_url_format, input_formats=[datetime_url_format])
    speakers = serializers.PrimaryKeyRelatedField(many=True, queryset=Speaker.objects.all())
    activity_type = serializers.ChoiceField(choices=TalkActivityType.choices, default=TalkActivityType.PRESENTATION)

    class Meta:
        model = Talk
        fields = '__all__'
        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True, 'help_text': 'Opcional'},
        }
