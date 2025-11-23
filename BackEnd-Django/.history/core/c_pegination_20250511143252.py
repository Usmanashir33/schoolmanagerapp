from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 5  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow client to set page size with this query parameter
    max_page_size = 10  # Maximum limit for page size
    