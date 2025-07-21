from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from services.gifts.models import Gift
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
import uuid

class ListRetrieveGiftsViewTestCase(APITestCase):
    def setUp(self):
        # Cria alguns presentes
        self.gift1 = Gift.objects.create(
            id=uuid.uuid4(),
            name="Camiseta do evento",
            description="Camiseta exclusiva do evento",
            min_presence=1,
            total_amount=100,
            balance=100
        )
        self.gift2 = Gift.objects.create(
            id=uuid.uuid4(),
            name="Caneca personalizada",
            description="Caneca com o logo do evento",
            min_presence=2,
            total_amount=50,
            balance=50
        )
        self.gift3 = Gift.objects.create(
            id=uuid.uuid4(),
            name="Boné do evento",
            description="Boné estiloso do evento",
            min_presence=3,
            total_amount=30,
            balance=30
        )

        self.url = reverse('list-retrieve-gifts')

    def test_list_gifts(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['name'], "Camiseta do evento")
        self.assertEqual(response.data[1]['name'], "Caneca personalizada")
        self.assertEqual(response.data[2]['name'], "Boné do evento")

    def test_retrieve_gift_id(self):
        gift_id = self.gift1.id
        url = self.url + "?id=" + str(gift_id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], "Camiseta do evento")
        self.assertEqual(response.data[0]['min_presence'], 1)

    def test_retrieve_gift_name(self):
        gift_name = self.gift2.name
        url = self.url + "?name=" + gift_name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], "Caneca personalizada")