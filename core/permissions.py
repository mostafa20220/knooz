# carts/permissions.py
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from users.models import CUSTOMER, SELLER


class ReadOnly(BasePermission):
    message = 'You do not have permission to perform this action. Read only.'

    def has_permission(self, request, view):
        return request.method in ['GET', 'HEAD', 'OPTIONS']

class IsCustomer(BasePermission):
    message = 'You do not have permission to perform this action. Only customers are allowed.'

    def has_permission(self, request, view):
        if not (request.user.is_authenticated and request.user.user_type == CUSTOMER):
            raise PermissionDenied(self.message)
        return True

class IsSeller(BasePermission):
    message = 'You do not have permission to perform this action. Only sellers are allowed.'

    def has_permission(self, request, view):
        if not (request.user.is_authenticated and request.user.user_type == SELLER):
            raise PermissionDenied(self.message)
        return True