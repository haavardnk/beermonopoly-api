from rest_framework.pagination import PageNumberPagination

class Pagination(PageNumberPagination):
    page_size = 25