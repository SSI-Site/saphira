from django.urls.conf import path

from .views import AdminDestroyPresenceView, AdminListCreatePresenceView

urlpatterns = [
    path("<talk_id>/<student_document>", AdminDestroyPresenceView.as_view(), name="admin-destroy-presence"),
    path("", AdminListCreatePresenceView.as_view(), name="admin-list-create-presence"),
]
