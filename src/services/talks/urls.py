from django.urls.conf import path

from .views import (
    AdminListCreateTalksView,
    AdminRetrieveUpdateDestroyTalkView,
    AdminListCreateSponsorView,
    AdminRetrieveUpdateDestroySponsorView,
    ListRetrieveTalksView
)

talks_urls = [
    path('', ListRetrieveTalksView.as_view(), name='talks-list'),
]

admin_talks_urls = [
    path("", AdminListCreateTalksView.as_view(), name="admin-list-create-talks"),
    path("<int:pk>", AdminRetrieveUpdateDestroyTalkView.as_view(), name="admin-retrieve-update-destroy-talk"),
    path("sponsors/", AdminListCreateSponsorView.as_view(), name="admin-list-create-sponsors"),
    path("sponsors/<int:pk>", AdminRetrieveUpdateDestroySponsorView.as_view(), name="admin-retrieve-update-destroy-sponsor"),
]

urlpatterns = talks_urls
