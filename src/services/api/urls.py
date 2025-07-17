from django.urls import path, register_converter
from django.urls.conf import include

from api import views
from api.utils import UUIDConverter

from .views import *
from students.urls import admin_students_urls, admin_student_urls

register_converter(UUIDConverter, 'uuid')

urlpatterns = [
    # Public endpoints
    path('', views.index, name='index'),
    path('speakers', RetrieveSpeakersView.as_view(), name='list-speakers'),
    path('speakers/<str:name>', RetrieveSpeakerByNameView.as_view(), name='retrieve-speaker-by-name'),
    path('admin/login', AdminLoginView.as_view(), name='admin-login'),
    path('admin/logout', AdminLogoutView.as_view(), name='admin-logout'),
    path('gifts', ListRetrieveGiftsView.as_view(), name='list-retrieve-gifts'),

    path('student', include('students.urls')),
    # Admin endpoints
    path('admin', views.admin_index, name='admin-login-test'),
    path('admin/talks', AdminListCreateTalksView.as_view(), name='admin-list-create-talks'),
    path('admin/talk/<int:pk>', AdminRetrieveUpdateDestroyTalkView.as_view(), name='admin-retrieve-update-destroy-talk'),
    path('admin/tokens', AdminListCreateTokensView.as_view(), name='admin-list-create-tokens'),
    path('admin/presences', AdminListCreatePresenceView.as_view(), name='admin-list-create-presence'),
    path('admin/presence/<talk_id>/<student_document>', AdminDestroyPresenceView.as_view(), name='admin-destroy-presence'),
    path('admin/<talk_id>/draw', AdminDrawOnTalkView.as_view(), name='admin-draw-on-talk'),
    path('admin/speakers/<uuid:speaker_id>', AdminUpdateDestroySpeakerView.as_view(), name='admin-update-destroy-speaker'),
    path('admin/speakers', AdminCreateSpeakerView.as_view(), name='admin-create-speaker'),
    path('admin/gifts', AdminListCreateGiftsView.as_view(), name='admin-list-create-gifts'),
    path('admin/gifts/<uuid:id>', AdminUpdateDestroyGiftView.as_view(), name='admin-update-destroy-gift'),
    path('admin/winners', AdminListWinnerView.as_view(), name='admin-list-draw-winners'),
    path('admin/winners/<uuid:student_id>', AdminDestroyWinnerView.as_view(), name='admin-destroy-winner'),

    path('admin/students', include(admin_students_urls)),
    path('admin/student', include(admin_student_urls)),

    # path('admin/attendance-report', AdminAttendanceReportView.as_view(), name='admin-attendance-report'),
    # TODO: fazer tudo relacionado aos brindes
]
