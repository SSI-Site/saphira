from rest_framework.pagination import PageNumberPagination

class StudentPagination(PageNumberPagination):
    """Paginação das listagens de estudantes.

    Parâmetros aceitos na URL:
    - `page`: página desejada, começando em 1. Ex: /admin/students/?page=2
    - `size`: quantidade de estudantes por página. Ex: /admin/students/?size=50

    O tamanho padrão da página é 20 e o máximo permitido é 100.
    """
    page_size = 20
    page_query_param = 'page'
    page_size_query_param = 'size'
    max_page_size = 100
