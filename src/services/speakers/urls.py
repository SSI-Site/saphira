from django.urls import path
from .views import *

speakers_urls = [
    path('', RetrieveSpeakersView.as_view(), name='list-speakers'),
]

speaker_urls = [
    path('<uuid:speakerId>/schedule', RetrieveSpeakerSchedule.as_view(), name='retrieve-speaker-schedule'),
    path('<str:name>', RetrieveSpeakerByNameView.as_view(), name='retrieve-speaker-by-name'),
]

admin_speakers_urls = [
    path('', AdminCreateSpeakerView.as_view(), name='admin-create-speaker'),
]

admin_speaker_urls = [
    path('<uuid:speaker_id>', AdminUpdateDestroySpeakerView.as_view(),
         name='admin-update-destroy-speaker'),
]

urlpatterns = speakers_urls
