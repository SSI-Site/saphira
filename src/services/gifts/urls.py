from django.urls import path
from . import views

gifts_urls = [
    path('', views.ListRetrieveGiftsView.as_view(), name='list-retrieve-gifts'),
]

admin_gifts_urls = [
    path('', views.AdminListCreateGiftsView.as_view(), name='admin-list-create-gifts'),
    path('<uuid:id>', views.AdminUpdateDestroyGiftView.as_view(), name='admin-update-destroy-gift'),
]

urlpatterns = gifts_urls