from django.urls import path, register_converter
from django.urls.conf import include

from services.api import views
from services.api.views import *

from services.api.utils import UUIDConverter
from services.gifts.urls import admin_gifts_urls
from services.speakers.urls import admin_speakers_urls, admin_speaker_urls, speaker_urls
from services.students.urls import admin_students_urls, admin_student_urls

register_converter(UUIDConverter, 'uuid')

urlpatterns = [
    # Public endpoints
    path('', views.index, name='index'),
    path('admin/login', AdminLoginView.as_view(), name='admin-login'),
    path('admin/logout', AdminLogoutView.as_view(), name='admin-logout'),

    path('student/', include('services.students.urls')),
    path('gifts/', include('services.gifts.urls')),
    path('speakers/', include('services.speakers.urls')),
    path('speaker/', include(speaker_urls)),

    # Admin endpoints
    path('admin', views.admin_index, name='admin-login-test'),
    path('admin/talks', AdminListCreateTalksView.as_view(), name='admin-list-create-talks'),
    path('admin/talk/<int:pk>', AdminRetrieveUpdateDestroyTalkView.as_view(), name='admin-retrieve-update-destroy-talk'),
    path('admin/tokens', AdminListCreateTokensView.as_view(), name='admin-list-create-tokens'),
    path('admin/presences', AdminListCreatePresenceView.as_view(), name='admin-list-create-presence'),
    path('admin/presence/<talk_id>/<student_document>', AdminDestroyPresenceView.as_view(), name='admin-destroy-presence'),
    path('admin/<talk_id>/draw', AdminDrawOnTalkView.as_view(), name='admin-draw-on-talk'),
    path('admin/winners', AdminListWinnerView.as_view(), name='admin-list-draw-winners'),
    path('admin/winners/<uuid:winner_id>', AdminDestroyWinnerView.as_view(), name='admin-destroy-winner'),
    path('admin/winners/students/<uuid:student_id>', AdminRetrieveWinnerByStudentView.as_view(), name='admin-retrieve-winner-by-student'),
    path('admin/winners/talks/<int:talk_id>', AdminListCreateWinner.as_view(), name='admin-list-create-winner'),

    path('admin/students/', include(admin_students_urls)),
    path('admin/student/', include(admin_student_urls)),
    path('admin/gifts/', include(admin_gifts_urls)),
    path('admin/speakers/', include(admin_speakers_urls)),
    path('admin/speakers/', include(admin_speaker_urls)),

    # path('admin/attendance-report', AdminAttendanceReportView.as_view(), name='admin-attendance-report'),
    # TODO: fazer tudo relacionado aos brindes
]
