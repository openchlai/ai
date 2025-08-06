from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict

class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination with page size control and metadata.
    Default page size: 20
    Max page size: 100
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('total_pages', self.page.paginator.num_pages),
            ('results', data)
        ]))

class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for large result sets.
    Default page size: 100
    Max page size: 500
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500

class CompactResultsSetPagination(PageNumberPagination):
    """
    Compact pagination for small widgets or dropdowns.
    Default page size: 10
    Max page size: 50
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class CursorTimestampPagination(PageNumberPagination):
    """
    Cursor-based pagination using timestamps for infinite scroll.
    """
    ordering = '-created_at'
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100

class ContactsPagination(StandardResultsSetPagination):
    """
    Specialized pagination for Contacts with optimized defaults.
    """
    page_size = 25
    max_page_size = 200

class DynamicPagination(PageNumberPagination):
    """
    Smart pagination that adapts to different devices.
    Desktop: larger page size
    Mobile: smaller page size
    """
    def get_page_size(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if 'mobile' in user_agent:
            return min(20, self.max_page_size)
        return min(50, self.max_page_size)

    page_size_query_param = 'page_size'
    max_page_size = 100