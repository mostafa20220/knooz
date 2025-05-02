# pagination.py
from rest_framework.pagination import CursorPagination

class CustomCursorPagination(CursorPagination):
    ordering = "-created_at"  # Descending order by 'created_at'
    page_size = 10  # Optional: Override default page size here