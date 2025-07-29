from django.urls import path, register_converter
from django.urls.conf import include

from services.api import views
from services.api.views import *

from services.api.utils import UUIDConverter
from services.gifts.urls import admin_gifts_urls
from services.speakers.urls import admin_speakers_urls, admin_speaker_urls, speaker_urls
from services.students.urls import admin_students_urls, admin_student_urls
from services.talks.urls import admin_talks_urls

register_converter(UUIDConverter, 'uuid')

urlpatterns = [
    # Public endpoints
    path('', views.index, name='index'),
    path('admin/login', AdminLoginView.as_view(), name='admin-login'),
    path('admin/logout', AdminLogoutView.as_view(), name='admin-logout'),

    path('student/', include('services.students.urls')),
    path('gifts/', include('services.gifts.urls')),
    path('speakers/', include('services.speakers.urls')),
    path('talks/', include('services.talks.urls')),
    path('speaker/', include(speaker_urls)),

    # Admin endpoints
    path('admin', views.admin_index, name='admin-login-test'),
    path('admin/students/', include(admin_students_urls)),
    path('admin/student/', include(admin_student_urls)),
    path('admin/gifts/', include(admin_gifts_urls)),
    path('admin/talks/', include(admin_talks_urls)),
    path('admin/presences', include('services.presences.urls')),
    path('admin/speakers/', include(admin_speakers_urls)),
    path('admin/speakers/', include(admin_speaker_urls)),
    path('admin/winners/', include('services.winners.urls')),
    # path('admin/attendance-report', AdminAttendanceReportView.as_view(), name='admin-attendance-report'),
    # TODO: fazer tudo relacionado aos brindes
]
