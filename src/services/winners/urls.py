from django.urls import path
from .views import (
    AdminDestroyWinnerView,
    AdminDrawOnTalkView,
    AdminListCreateWinner,
    AdminListWinnerView,
    AdminRetrieveWinnerByStudentView,
    AdminRetrieveWinnerByTalkView,
)


urlpatterns = [
    path('<talk_id>/draw', AdminDrawOnTalkView.as_view(), name='admin-draw-on-talk'),
    path('', AdminListWinnerView.as_view(), name='admin-list-draw-winners'),
    path('<uuid:winner_id>', AdminDestroyWinnerView.as_view(), name='admin-destroy-winner'),
    path('students/<uuid:student_id>', AdminRetrieveWinnerByStudentView.as_view(), name='admin-retrieve-winner-by-student'),
    path('talks/<int:talk_id>', AdminListCreateWinner.as_view(), name='admin-list-create-winner'),
    path('talk/<int:talk_id>', AdminRetrieveWinnerByTalkView.as_view(), name="admin-retrieve-winner-by-talk"),
]
