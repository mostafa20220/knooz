from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, SAFE_METHODS

from users.models import SELLER

class IsSellerOrReadOnly(BasePermission):
    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):

        # Allow read-only access for any user
        if request.method in SAFE_METHODS:
            return True

        # Allow to create, update, and delete access only for users of type SELLER
        if not (request.user.is_authenticated and request.user.user_type == SELLER):
            raise PermissionDenied(self.message)
        return True
