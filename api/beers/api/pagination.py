from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    page_size = 25
    max_page_size = 100
    page_size_query_param = "page_size"


class LargeResultPagination(PageNumberPagination):
    page_size = 25
    max_page_size = 1000
    page_size_query_param = "page_size"
