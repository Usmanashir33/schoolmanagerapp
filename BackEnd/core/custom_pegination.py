from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination50(PageNumberPagination):
    page_size = 50  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow client to set page size with this query parameter
    max_page_size = 10  # Maximum limit for page size
    page_query_param = "page"
    
    def get_paginated_response(self, data):
        return {
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "current_page": self.page.number,

            "next": self.get_next_link(),
            "previous": self.get_previous_link(),

            "has_next": self.page.has_next(),
            "has_previous": self.page.has_previous(),

            "results": data
        }
    
class CustomPagination20(PageNumberPagination):
    page_size = 20  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow client to set page size with this query parameter
    max_page_size = 10  # Maximum limit for page size
    page_query_param = "page"
    
class CustomPagination30(PageNumberPagination):
    page_size = 30  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow client to set page size with this query parameter
    max_page_size = 10 # Maximum limit for page size
    page_query_param = "page"
    
class CustomPagination100(PageNumberPagination):
    page_size = 100  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow client to set page size with this query parameter
    max_page_size = 10  # Maximum limit for page size
    page_query_param = "page"
    
