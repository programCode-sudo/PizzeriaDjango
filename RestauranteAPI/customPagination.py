from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  # Número de resultados por página
    page_size_query_param = 'page_size'  # Parámetro de consulta para cambiar el tamaño de la página
    max_page_size = 100  # Tamaño máximo de página que se puede solicitar