from django.urls import path, register_converter

from api import views
from api.utils import UUIDConverter

from .views import *

register_converter(UUIDConverter, 'uuid')

urlpatterns = [
    # Public endpoints
    path('', views.index, name='index'),
    path('speakers', RetrieveSpeakersView.as_view(), name='list-speakers'),
    path('speakers/<str:name>', RetrieveSpeakerByNameView.as_view(), name='retrieve-speaker-by-name'),
    path('admin/login', AdminLoginView.as_view(), name='admin-login'),
    path('admin/logout', AdminLogoutView.as_view(), name='admin-logout'),

    # Firebase endpoints (student)
    path('student/login', StudentLogin.as_view(), name='student-login'),

    # Student endpoints
    path('student/<uuid:student_id>', StudentRetrieveUpdateView.as_view(), name='student-retrieve-update'),
    path('student/<uuid:student_id>/presence', CreateStudentOnlinePresenceView.as_view(), name='create-student-online-presence'),
    path('student/<uuid:student_id>/presences', RetrieveStudentPresencesView.as_view(), name='retrieve-student-presences'),

    # Admin endpoints
    path('admin', views.admin_index, name='admin-login-test'),
    path('admin/students', AdminListStudentsView.as_view(), name='admin-list-students'),
    path('admin/students/search/<name>', AdminListStudentsByNameView.as_view(), name='admin-list-students-by-name'),
    path('admin/student/<student_document>', AdminRetrieveStudentInfoView.as_view(), name='admin-retrieve-student-info'),
    path('admin/students/<student_document>', AdminDestroyStudentView.as_view(), name='admin-destroy-student'),
    path('admin/talks', AdminListCreateTalksView.as_view(), name='admin-list-create-talks'),
    path('admin/talk/<int:pk>', AdminRetrieveUpdateDestroyTalkView.as_view(), name='admin-retrieve-update-destroy-talk'),
    path('admin/tokens', AdminListCreateTokensView.as_view(), name='admin-list-create-tokens'),
    path('admin/presences', AdminListCreatePresenceView.as_view(), name='admin-list-create-presence'),
    path('admin/presence/<talk_id>/<student_document>', AdminDestroyPresenceView.as_view(), name='admin-destroy-presence'),
    path('admin/<talk_id>/draw', AdminDrawOnTalkView.as_view(), name='admin-draw-on-talk'),
    path('admin/speakers/<uuid:speaker_id>', AdminUpdateDestroySpeakerView.as_view(), name='admin-update-destroy-speaker'),
    path('admin/speakers', AdminCreateSpeakerView.as_view(), name='admin-create-speaker'),
    path('admin/gifts', AdminListCreateGiftsView.as_view(), name='admin-list-create-gifts'),

    # path('admin/attendance-report', AdminAttendanceReportView.as_view(), name='admin-attendance-report'),
    # TODO: fazer tudo relacionado aos brindes
]
