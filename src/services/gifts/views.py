from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from django.db import models
from rest_framework.response import Response

from .models import Gift
from .serializers import GiftPublicSerializer, GiftSerializer
from .utils import check_and_remove_gifts_from_gift
from ..api.decorators import admin_auth_required

############################################################################################################
#                                             PUBLIC VIEWS
############################################################################################################

class ListRetrieveGiftsView(generics.ListAPIView):
    """
    Lista todos os brindes.

    Você pode filtrar a lista usando os seguintes parâmetros na URL:
    - `id`: Filtra por um ID exato. Ex: /gifts/?id=1
    - `name`: Filtra por brindes cujo nome começa com o texto. Ex: /api/gifts/?name=Can
    """
    serializer_class = GiftPublicSerializer

    def get_queryset(self):
        """
        Este método constrói a lista de objetos dinamicamente.
        """
        queryset = Gift.objects.all()

        gift_id = self.request.query_params.get('id')
        name_query = self.request.query_params.get('name')

        if gift_id:
            queryset = queryset.filter(id=gift_id)

        if name_query:
            queryset = queryset.filter(name__startswith=name_query)

        return queryset

############################################################################################################
#                                               ADMIN VIEWS
############################################################################################################

@method_decorator(admin_auth_required, name='dispatch')
class AdminListCreateGiftsView(generics.ListCreateAPIView):
    serializer_class = GiftPublicSerializer
    def post(self, request, *args, **kwargs):
        serializer = GiftSerializer(data=request.data)

        if serializer.is_valid():
            gift = serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """
        Este método constrói a lista de objetos dinamicamente.
        """
        queryset = Gift.objects.all()

        gift_id = self.request.query_params.get('id')
        name_query = self.request.query_params.get('name')

        if gift_id:
            queryset = queryset.filter(id=gift_id)

        if name_query:
            queryset = queryset.filter(name__startswith=name_query)

        return queryset

@method_decorator(admin_auth_required, name='dispatch')
class AdminUpdateDestroyGiftView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GiftSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Gift.objects.all()

    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)
        gift = self.get_queryset().filter(id=lookup_value).first()

        if not gift:
            raise Http404(f"Gift com id {lookup_value} não encontrado.")
        return gift

    def delete(self, request, *args, **kwargs):
        gift = self.get_object()
        gift.delete()
        return Response({'message': f'Gift {gift.name} removido com sucesso.'}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        gift = self.get_object()
        allowed_fields = ['name', 'description', 'total_amount', 'min_presence']

        for field in allowed_fields:
            if field in request.data:
                setattr(gift, field, request.data[field])

        gift.save()

        # Caso o minPresence tenha sido alterado, validar os StudentGifts para que apenas estudantes com presenças mínimas o tenham
        check_and_remove_gifts_from_gift(gift)

        return Response({
            'id': gift.id,
            'name': gift.name,
            'description': gift.description,
            'min_presence': gift.min_presence,
            'total_amount': gift.total_amount,
            'balance': gift.balance
        })
