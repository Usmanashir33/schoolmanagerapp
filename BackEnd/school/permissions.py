from rest_framework.permissions import BasePermission
from rest_framework.exceptions import APIException

class PermissionDenied(APIException):
    status_code = 202
    default_detail = {"error": "Permission denied !."}
    default_code = "permission_denied" 
    
class SchoolPermissions:
    # Students
    CAN_VIEW_STUDENTS = "can_view_students"
    CAN_ADD_STUDENTS = "can_add_students"
    CAN_MANAGE_STUDENTS = "can_manage_students"
    STUDENTS_MANAGEMENT = "students_management"

    # Teachers
    CAN_VIEW_TEACHERS = "can_view_teachers"
    CAN_ADD_TEACHERS = "can_add_teachers"
    CAN_MANAGE_TEACHERS = "can_manage_teachers"
    TEACHERS_MANAGEMENT = "teachers_management"
    

    # Staffs
    CAN_VIEW_STAFFS = "can_view_staffs"
    CAN_ADD_STAFFS = "can_add_staffs"
    CAN_MANAGE_STAFFS = "can_manage_staffs"
    STAFFS_MANAGEMENT = "staffs_management"

    # School
    CAN_MANAGE_SCHOOL = "can_manage_school"

    # Academics
    CAN_MANAGE_ACADEMICS = "can_manage_academics"

    # Finance
    CAN_MANAGE_FINANCE = "can_manage_finance"
    CAN_MANAGE_PAYMENTS = "can_manage_payments"

    # Results
    CAN_ADD_RESULTS = "can_add_results"
    CAN_VIEW_RESULTS = "can_view_results"
    CAN_MANAGE_RESULTS = "can_manage_results"


class HasSchoolPermission(BasePermission):

    def has_permission(self, request, view):
        school_id = view.kwargs.get('school_id') or request.data.get('school')or request.data.get('school_id') or request.query_params.get('school_id') or request.query_params.get('school')
        required_permissions = getattr(
            view,
            "required_permissions",
            []
        )
        user = request.user
        if not user.school_role or not str(user.school.id) == str(school_id) :
            raise PermissionDenied()
        
        if not user.is_authenticated:
            raise PermissionDenied()
        

        # Director bypass  letter 
        
        # if user.role  == "Director":
        #     return True

        if not required_permissions:
            return True

        return user.has_permission(required_permissions)