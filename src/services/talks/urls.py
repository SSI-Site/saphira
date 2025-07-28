from django.urls.conf import path

from .views import *

talks_urls = [
    path('', ListRetrieveTalksView.as_view(), name='talks-list'),
]

admin_talks_urls = [
    path("", AdminListCreateTalksView.as_view(), name="admin-list-create-talks"),
    path("<int:pk>", AdminRetrieveUpdateDestroyTalkView.as_view(), name="admin-retrieve-update-destroy-talk"),
]

urlpatterns = talks_urls
