from rest_framework import serializers

from services.api.utils import datetime_url_format
from services.speakers.models import Speaker
from .models import Talk, TalkActivityType, Sponsor, TalkModeType

class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsor
        fields = ['id', 'name', 'url']

class TalkSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format=datetime_url_format, input_formats=[datetime_url_format])
    end_time = serializers.DateTimeField(format=datetime_url_format, input_formats=[datetime_url_format])
    speakers = serializers.PrimaryKeyRelatedField(many=True, queryset=Speaker.objects.all())
    activity_type = serializers.ChoiceField(choices=TalkActivityType.choices, default=TalkActivityType.PRESENTATION)
    mode = serializers.ChoiceField(choices=TalkModeType.choices, default=TalkModeType.IN_PERSON)
    sponsor = SponsorSerializer(read_only=True)
    sponsor_id = serializers.PrimaryKeyRelatedField(queryset=Sponsor.objects.all(), write_only=True, source='sponsor', required=False, allow_null=True)

    class Meta:
        model = Talk
        fields = '__all__'
        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True, 'help_text': 'Opcional'},
            'sponsor_id': {'required': False, 'allow_blank': True, 'help_text': 'Opcional'},
        }
