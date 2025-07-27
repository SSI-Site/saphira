from django.urls.conf import path

from .views import (
    AdminListCreateTalksView,
    AdminRetrieveUpdateDestroyTalkView
)

urlpatterns = [
    path("", AdminListCreateTalksView.as_view(), name="admin-list-create-talks"),
    path("<int:pk>", AdminRetrieveUpdateDestroyTalkView.as_view(), name="admin-retrieve-update-destroy-talk"),
]
