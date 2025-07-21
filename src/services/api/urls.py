from django.urls import path, register_converter
from django.urls.conf import include

from services.api import views
from services.api.views import *

from services.api.utils import UUIDConverter

register_converter(UUIDConverter, 'uuid')

urlpatterns = [
    # Public endpoints
    path('', views.index, name='index'),
    path('speakers', RetrieveSpeakersView.as_view(), name='list-speakers'),
    path('speakers/<str:name>', RetrieveSpeakerByNameView.as_view(), name='retrieve-speaker-by-name'),
    path('admin/login', AdminLoginView.as_view(), name='admin-login'),
    path('admin/logout', AdminLogoutView.as_view(), name='admin-logout'),

    path('student/', include('services.students.urls')),
    path('gifts/', include('services.gifts.urls')),
    # Admin endpoints
    path('admin', views.admin_index, name='admin-login-test'),
    path('admin/talks', AdminListCreateTalksView.as_view(), name='admin-list-create-talks'),
    path('admin/talk/<int:pk>', AdminRetrieveUpdateDestroyTalkView.as_view(), name='admin-retrieve-update-destroy-talk'),
    path('admin/tokens', AdminListCreateTokensView.as_view(), name='admin-list-create-tokens'),
    path('admin/presences', AdminListCreatePresenceView.as_view(), name='admin-list-create-presence'),
    path('admin/presence/<talk_id>/<student_document>', AdminDestroyPresenceView.as_view(), name='admin-destroy-presence'),
    path('admin/<talk_id>/draw', AdminDrawOnTalkView.as_view(), name='admin-draw-on-talk'),
    path('admin/speaker/<uuid:speaker_id>', AdminUpdateDestroySpeakerView.as_view(), name='admin-update-destroy-speaker'),
    path('admin/speakers', AdminCreateSpeakerView.as_view(), name='admin-create-speaker'),
    path('admin/winners', AdminListWinnerView.as_view(), name='admin-list-draw-winners'),
    path('admin/winners/<uuid:student_id>', AdminDestroyWinnerView.as_view(), name='admin-destroy-winner'),

    path('admin/students/', include('services.students.urls')),
    path('admin/student/', include('services.students.urls')),
    path('admin/gifts/', include('services.gifts.urls')),

    # path('admin/attendance-report', AdminAttendanceReportView.as_view(), name='admin-attendance-report'),
    # TODO: fazer tudo relacionado aos brindes
]
