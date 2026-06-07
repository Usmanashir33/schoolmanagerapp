
from django.utils import timezone

from django.db.models import Q

# core app
# views.py or any view file
from authUser.models import User
from attendanceanddevices.models import User
from core.emails.email_templates.emails import generate_staff_role_assignment_email
from core.formatters import format_serializer_errors
from core.permissions import DirectorUserPermission

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from core.tasks import send_html_email
from school.models import School 
from school.permissions import HasSchoolPermission, SchoolPermissions
from school.tasks import SchoolServices
from staff.serializers import StaffDetailSerializer,StaffCreateUpdateSerializer,StaffSerializer
from staff.models import Staff

from core.custom_pegination import CustomPagination15
from academics.models import ClassRoom
from school.models import School

from school.models import ActivityLog, School
from school.serializers import ActivityLogSerializer
from django.core.cache import cache


#==================================================================================================            
#                                       STAFF SECTION                           
#==================================================================================================
class AllStaffsView(APIView): #paginated request
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_VIEW_STAFFS]
    
    # ---------------- GET  ALL Staff -----------------
    def get(self, request,school_id):  
        try:
            # get all staffs of the school
            page = request.query_params.get("page", 1)
            cache_key = f"staffs_{school_id}_page_{page}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response:
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
    
            staffs  = Staff.objects.filter(school_id = school_id).select_related(
                'user',
                'activity_role'
            ).order_by("joined_at")
            
            paginator = CustomPagination15()

            paginated_students = paginator.paginate_queryset(
                staffs,
                request
            )

            serializer = StaffSerializer(
                paginated_students,
                many=True
            ).data

            resp=paginator.get_paginated_response({
                "success": "School staffs", 
                "paginated_data": serializer
            })
            try :
                cache.set(cache_key,resp,timeout=60*5) # Cache for 5 minutes)
            except :
                pass
            return Response(resp, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

class FilterStaffView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_VIEW_STAFFS]
    # ---------------- SEARCH Staff -----------------
    def get(self, request,school_id,searchQuery):  
        try:
            searched  = Staff.objects.filter(
                Q(first_name__icontains = searchQuery) |  Q(title__icontains = searchQuery) |
                Q(last_name__icontains = searchQuery)  | Q(middle_name__icontains = searchQuery) | Q(email__icontains = searchQuery) |
                Q(phone__icontains = searchQuery) | Q(staff_id__icontains = searchQuery)
            ).filter(school_id = school_id).select_related('user','activity_role')[:5]
            
            if not searched:
                return Response({"success": "not found"}, status=status.HTTP_200_OK)
            serializer = StaffSerializer(searched,many=True)
            return Response({
                    "success": "searchResults",
                    "results": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
class StaffCreateUpdateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_STAFFS]
    
    # ---------------- GET Staff -----------------
    def get(self, request ,school_id,staff_id):  
        try:
            cache_key = f"staff_{staff_id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            valid_staff  = Staff.objects.filter(id = staff_id, school_id=school_id).select_related(
                "user",'activity_role'
            ).first()  
            if not valid_staff:
                return Response({"error": "staff not found"}, status=status.HTTP_200_OK)
            serializer = StaffDetailSerializer(valid_staff)
            resp = {
                    "success": "staff details",
                    "staff_details": serializer.data
            }
            try :
                cache.set(cache_key,resp,timeout=60*3)
            except :
                pass
            return Response(resp, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
            
    def post(self, request):   ## add new staff 
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            email = request.data.get( "email" )
            phone = request.data.get( "phone" )

            # if not request.user.pins.checkPin(pin) :
            #     return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            valid_school = School.objects.filter(id=school_id).first()  
            if not valid_school:
                return Response({"error": "Invalid  Entry"}, status=status.HTTP_200_OK)
            
            existed_staff = User.objects.filter(
                Q(email__iexact = email) | 
                Q(phone_number__iexact=phone)
                ).values(
                    "email",
                    "phone_number"
                ).first()

            if existed_staff : 
                if existed_staff.get("email", "not provided").lower() == email.lower():
                    return Response({"error": "staff email is already used!"},status=status.HTTP_200_OK)
                
                if existed_staff.get("phone_number", "not provided ").lower() == phone.lower():
                    return Response({"error": "staff phone number is already used!"},status=status.HTTP_200_OK)

            serializer = StaffCreateUpdateSerializer(data=request.data,context = {"request":request}) 
            if serializer.is_valid():
                serializer.save() 
                
                return Response({
                    "success": "staff created successfully",
                    "new_staff": StaffSerializer(serializer.instance).data
                }, status=status.HTTP_200_OK)
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error!"}, status=status.HTTP_200_OK)

    # ---------------- UPDATE staff -----------------
    def put(self, request,staff_id):
        try : 
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            email = request.data.get( "email" )
            phone = request.data.get( "phone" )
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
             # validate director actions 
            valid_school = School.objects.filter(id=school_id).first()  
            if not valid_school:
                return Response({"error": "Invalid  Entry"}, status=status.HTTP_200_OK)

            staff = Staff.objects.filter(
                id=staff_id, school_id=school_id
            ).first()
            if not staff:
                return Response({"error": "staff not found"}, status=status.HTTP_200_OK)
            existed_staff = User.objects.filter(
                Q(email__iexact = email) | 
                Q(phone_number__iexact=phone)
                ).exclude(id=staff.user.id).values(
                    "email",
                    "phone_number"
                ).first()

            if existed_staff : 
                if existed_staff.get("email", "not provided").lower() == email.lower():
                    return Response({"error": "staff new email is already used!"},status=status.HTTP_200_OK)
                
                if existed_staff.get("phone_number", "not provided ").lower() == phone.lower():
                    return Response({"error": "staff new phone number is already used!"},status=status.HTTP_200_OK)
    
            serializer = StaffCreateUpdateSerializer(staff, data=request.data,partial=True,context = {"request":request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": "staff updated successfully" ,
                    "updated_staff": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error!"}, status=status.HTTP_200_OK)

class StaffAdministrationView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_STAFFS]
    
    def post(self, request,staff_id,request_action):
        try:
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
             # validate director actions 
            valid_school = School.objects.filter(id=school_id).first()  #.exists()
            if not valid_school:
                return Response({"error": "Invalid  Entry"}, status=status.HTTP_200_OK)

            staff = Staff.objects.filter(
                id=staff_id,
                school_id=school_id
            ).first()

            if not staff:
                return Response({"error": "Staff not found "}, status=status.HTTP_200_OK)
            # ---------------- DELETE STAFF -----------------
            if request_action == "delete":
                staff.delete()
                 # configuring activity log data 
                new_log = ActivityLog.objects.create(
                    school = valid_school ,
                    user=request.user,
                    action="DELETE",
                    module="STAFF",
                    description=f"{staff.staff_id} - {staff.full_name()}"
                )
                user_room = f"room{request.user.id}"
                log_data = ActivityLogSerializer(new_log).data
                data = {
                    "type": "send_response1",
                    "activity_log": log_data,
                    }
                try:
                    SchoolServices.send_activity_log.delay(destination=user_room, data=data)
                except :
                    pass
                return Response({
                    "success": f"Staff {request_action} successfully",
                    "del_staff": {'id': staff_id, "full_name": staff.full_name()}
                }, status=status.HTTP_200_OK)
            # ---------------- SUSPEND / ACTIVATE  STAFF -----------------
            if request_action == "suspend":
                user = staff.user
                user.is_active = not user.is_active
                user.save()
                request_action = "Activated" if user.is_active else "Suspended" 
                
                # configuring activity log data 
                new_log = ActivityLog.objects.create(
                    school = valid_school,
                    user=request.user,
                    action="UPDATE",
                    module="STAFF",
                    description=f"Staff {request_action}:{staff.staff_id} - {staff.full_name()}"
                )
                user_room = f"room{request.user.id}"
                log_data = ActivityLogSerializer(new_log).data
                data = {
                    "type": "send_response1",
                    "activity_log": log_data,
                    }
                try:
                    SchoolServices.send_activity_log.delay(destination=user_room, data=data)
                except :
                    pass
                return Response({
                    "success": f"Staff {request_action} successfully",
                    "sus_staff": {"id":staff_id,"is_active" :user.is_active}
                }, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
class StaffRoleManagementView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_SCHOOL]
    def put(self, request,staff_id,):
        try:
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            role_id =request.data.get("roleIds")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
             # validate director actions 
             
            valid_school = School.objects.filter(id=school_id).prefetch_related("roles").first()  #.exists()
            if not valid_school:
                return Response({"error": "Invalid  Entry"}, status=status.HTTP_200_OK)
            
            valid_role = valid_school.roles.filter(id__in=role_id).first()
            if not valid_role:
                return Response({"error": "Invalid  Role"}, status=status.HTTP_200_OK)
            
            staff = Staff.objects.filter(
                id=staff_id,
                school_id=school_id
            ).first()
            if not staff:
                return Response({"error": "Staff not found "}, status=status.HTTP_200_OK)
            serializer = StaffDetailSerializer(staff)
            
            if valid_role :
                user = staff.user
                user.school_role = valid_role
                user.save()
                request_action = f"{valid_role.name} Role Assigened" 
                
                 # configuring activity log data 
                new_log = ActivityLog.objects.create(
                    school = valid_school,
                    user=request.user,
                    action="UPDATE",
                    module="STAFF",
                    description=f"{request_action}:{staff.staff_id} - {staff.full_name()}"
                )
                user_room = f"room{request.user.id}"
                log_data = ActivityLogSerializer(new_log).data
                data = {
                    "type": "send_response1",
                    "activity_log": log_data,
                    }
                try :
                    SchoolServices.send_activity_log.delay(destination=user_room, data=data)
                    name = staff.full_name()
                    role_name = valid_role.name 
                    assigned_by = f"{request.user.role} {request.user.full_name()}"
                    
                    html_content = generate_staff_role_assignment_email(name,role_name,valid_school.name,assigned_by)
                    send_html_email.delay(
                        subject="School Role Promotion!",
                        to_email=staff.email,
                        html_content=html_content
                    )
                except :
                    pass
                
                return Response({
                    "success": f"Staff {request_action} successfully",
                    "updated_staff": serializer.data
                }, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
