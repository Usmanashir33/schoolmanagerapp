# permissions.py

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
# exceptions.py

from rest_framework.exceptions import APIException

class TransactionPermissionDenied(APIException):
    status_code = 202
    default_detail = {"error": "Transections suspended on this account !."}
    default_code = "permission_denied"

class StaffPermissionDenied(APIException):
    status_code = 403
    default_detail = {"error": "Access denied!."}
    default_code = "permission_denied"
    
class InactiveUserPermissionDenied(APIException):
    status_code = 403
    default_detail = {"error": "This account is inactive."}
    default_code = "permission_denied"

class CheckTransectionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise PermissionDenied({"error": "Login required."})

        if not getattr(request.user, 'can_transect', True):
            raise TransactionPermissionDenied()

        return True
class CheckStaffPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_staff:
            raise StaffPermissionDenied()
        return True
class CheckStaffPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_staff:
            raise StaffPermissionDenied()
        return True
    
