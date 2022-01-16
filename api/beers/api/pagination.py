from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    page_size = 25


class LargeResultPagination(PageNumberPagination):
    page_size = 500
