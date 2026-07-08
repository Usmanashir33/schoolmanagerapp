# permissions.py

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
# exceptions.py

from rest_framework.exceptions import APIException

class TransactionPermissionDenied(APIException):
    status_code = 202
    default_detail = {"error": "Transections suspended on this account !."}
    default_code = "permission_denied"
class DirectorPermissionDenied(APIException):
    status_code = 202
    default_detail = {"error": "Director permission denied !."}
    default_code = "permission_denied"
class StaffPermissionDenied(APIException):
    status_code = 202
    default_detail = {"error": "Staff permission denied !."}
    default_code = "permission_denied"
class TeacherPermissionDenied(APIException):
    status_code = 202
    default_detail = {"error": "Teacher permission denied !."}
    default_code = "permission_denied"
class ParentPermissionDenied(APIException):
    status_code = 202
    default_detail = {"error": "Parent permission denied !."}
    default_code = "permission_denied"

class CheckTransectionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise PermissionDenied({"error": "Login required."})
        
        # check if attribute vailable 
        if not getattr(request.user, 'can_transect', True):
            raise TransactionPermissionDenied()
        return True

class DirectorUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        school_id = view.kwargs.get('school_id') or request.data.get('school')or request.data.get('school_id') or request.query_params.get('school_id') or request.query_params.get('school')
        # check if user is teacher in any of the schools
        if not str(request.user.school_id) == str(school_id):
            raise DirectorPermissionDenied()
        if not getattr(request.user, 'director',None) :
            raise DirectorPermissionDenied()
        return True
class StaffUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        school_id = view.kwargs.get('school_id') or request.data.get('school')or request.data.get('school_id') or request.query_params.get('school_id') or request.query_params.get('school')
        # check if user is teacher in any of the schools
        if not str(request.user.school_id) == str(school_id):
            raise StaffPermissionDenied()
        if not getattr(request.user, 'staff',None) :
            raise StaffPermissionDenied()
        return True
class TeacherUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        school_id = view.kwargs.get('school_id') or request.data.get('school')or request.data.get('school_id') or request.query_params.get('school_id') or request.query_params.get('school')
        
        # check if user is teacher in any of the schools
        if not str(request.user.school_id) == str(school_id): 
            raise TeacherPermissionDenied()
        if not getattr(request.user, 'teacher',None) :
            raise TeacherPermissionDenied()
        return True
class ParentUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        school_id = view.kwargs.get('school_id') or request.data.get('school')or request.data.get('school_id') or request.query_params.get('school_id') or request.query_params.get('school')
        
        # check if user is parent in any of the schools
        if not str(request.user.school_id) == str(school_id): 
            raise ParentPermissionDenied()
        if not getattr(request.user, 'parent',None) :
            raise ParentPermissionDenied()
        return True
