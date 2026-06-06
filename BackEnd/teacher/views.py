from django.db.models import Q

# core app
# views.py or any view file
from core.formatters import format_serializer_errors
from core.permissions import DirectorUserPermission
from school.tasks import SchoolServices

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser , FormParser

from teacher.serializers import MiniTeacherSerializer, TeacherSerializer ,TeacherDetailSerializer,DisplinaryRecordSerializer,TeacherCreateSerializer
from teacher.models import Teacher 

from core.custom_pegination import CustomPagination15
from school.models import School
from school.permissions import HasSchoolPermission, SchoolPermissions
from authUser.models import User 
from django.core.cache import cache
from django.utils import timezone
from school.models import ActivityLog
from school.serializers import ActivityLogSerializer

#==================================================================================================            
#                                       TEACHER SECTION                           
#==================================================================================================
class AllTeachersView(APIView) : #paginated request
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_VIEW_TEACHERS]

    def get(self, request, school_id):
        try:
             # validate director actions
            valid_school = School.objects.filter(id=school_id).first()

            if not valid_school:
                return Response(
                    {"error": "Invalid Request"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            page = request.query_params.get("page", 1)
            cache_key = f"teachers_{school_id}_page_{page}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response:
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass

            teachers = (
                Teacher.objects
                .filter(school_id=valid_school.id)
                .select_related(
                    "user",
                    "bank_details"
                )
                .prefetch_related(
                    "disciplinaryRecords",
                )
                .order_by("-joined_at")
            ) 

            paginator = CustomPagination15()
            paginated_teachers = paginator.paginate_queryset(
                teachers,
                request
            )

            serializer = TeacherDetailSerializer(
                paginated_teachers,
                many=True
            ).data

            resp=paginator.get_paginated_response({
                "success": "School teachers", 
                "paginated_data": serializer
            })
            try :
                cache.set(cache_key,resp,timeout=60*5) # Cache for 5 minutes)
            except :
                pass
            return Response(resp, status=status.HTTP_200_OK)

        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
class ClassCurrentTeachersListView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [
        SchoolPermissions.CAN_VIEW_TEACHERS
    ]
    
    # ---------------- GET All Perticuler CLass TEACHER -----------------
    def get(self, request,school_id,class_id):  
        try:
             # find catched data before querying the database
            cache_key = f"teachers_{school_id}_{class_id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            
            class_students  = Teacher.objects.filter(school__id = school_id).filter(
                teaching_assignments__classroom__id = class_id,
            ).distinct()
            
            serializer = MiniTeacherSerializer(class_students,many=True) 
            resp={
                    "success": "All class teachers",
                    "classTeachers": serializer.data
            }
            try :
                cache.set(cache_key, resp, timeout=60*3)  # Cache for 3 minutes
            except :
                pass
            return Response(resp, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        

class FilterTeacherDetailView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_VIEW_TEACHERS]

    # ---------------- SERCH Teacher -----------------
    def get(self, request,school_id,searchQuery):  
        try:
            searched  = Teacher.objects.filter(
                Q(first_name__icontains = searchQuery) |  Q(title__icontains = searchQuery) |
                Q(last_name__icontains = searchQuery)  | Q(middle_name__icontains = searchQuery) | Q(email__icontains = searchQuery) |
                  Q(phone__icontains = searchQuery) | Q(staff_id__icontains = searchQuery)
            ).filter(school_id = school_id).select_related(
                    "user",
                    "bank_details"
                ).prefetch_related(
                    "disciplinaryRecords",
                )[:10]
            
            if not searched:
                return Response({"success": "not found"}, status=status.HTTP_200_OK)
            serializer = TeacherDetailSerializer(searched,many=True)
            return Response({
                    "success": "searchResults",
                    "results": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
class TeacherView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_TEACHERS]
    # ---------------- GET Teacher -----------------
    def get(self, request,school_id,teacher_id) :  
        try:
            cache_key = f"teacher_{teacher_id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            valid_teacher  = Teacher.objects.filter(id = teacher_id, school__id=school_id).select_related(
                'user','bank_details'    
            ).prefetch_related(
                "disciplinaryRecords",'teaching_assignments','form_classes'    
            ).first()  #.exists()
            if not valid_teacher:
                return Response({"error": "Teacher not found"}, status=status.HTTP_200_OK)
            serializer = TeacherDetailSerializer(valid_teacher) 
            resp = {
                    "success": "teacher details",
                    "teacher_details": serializer.data
            }
            try :
                cache.set(cache_key,resp,timeout=60*3)
            except :
                pass
            return Response(resp, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
            
    def post(self, request):   ## add new teacher 
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get("school")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
             # validate director actions 
            valid_school = School.objects.filter(id=school_id).first()
            if not valid_school:
                return Response({"error": "Invalid Entry"}, status=status.HTTP_200_OK)
            
            # authenticate new teacher 
            email = request.data.get('email','invalid')
            phone = request.data.get('phone','invalid')
            
            if  email== 'invalid' or  phone== 'invalid':
                return Response({"error": "Invalid email or phone number "}, status=status.HTTP_200_OK)
            
            existed = User.objects.filter(
                Q(email__iexact = email) | 
                Q(phone_number__iexact=phone)
                ).values(
                    "email",
                    "phone_number"
                ).first()

            if existed:
                if existed.get("email", "not provided").lower() == email.lower():
                    return Response({"error": "teacher email is already used!"},status=status.HTTP_200_OK)
                
                if existed.get("phone_number", "not provided ").lower() == phone.lower():
                    return Response({"error": "teacher phone number is already used!"},status=status.HTTP_200_OK)


            serializer = TeacherCreateSerializer(data=request.data,context = {"request":request}) 
            if serializer.is_valid():
                serializer.save() 
                return Response({
                    "success": "Teacher created successfully",
                    "new_teacher": TeacherSerializer(serializer.instance).data
                }, status=status.HTTP_200_OK)
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": str(e)}, status=status.HTTP_200_OK)

    # ---------------- UPDATE TEACHER -----------------
    def put(self, request,teacher_id):
        try : 
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(id=school_id).first()
            if not valid_school:
                return Response({"error": "Invalid Entry"}, status=status.HTTP_200_OK)
            
            teacher  = Teacher.objects.filter(id = teacher_id, school__id=school_id).select_related(
                'user','bank_details'    
            ).prefetch_related(
                "disciplinaryRecords",'teaching_assignments','form_classes'    
            ).first()
            if not teacher:
                return Response({"error": "Teacher not found"}, status=status.HTTP_200_OK)
            
            # authenticate new teacher 
            email = request.data.get('email','invalid')
            phone = request.data.get('phone','invalid')
            
            if  email== 'invalid' or  phone== 'invalid':
                return Response({"error": "Invalid email or phone number "}, status=status.HTTP_200_OK)
            
            existed_teacher = User.objects.filter(
                Q(email__iexact = email) | 
                Q(phone_number__iexact=phone)
                ).exclude(id=teacher.user.id).values(
                    "email",
                    "phone_number"
                ).first()

            if existed_teacher:
                if existed_teacher.get("email", "not provided").lower() == email.lower():
                    return Response({"error": "teacher new email is already used!"},status=status.HTTP_200_OK)
                
                if existed_teacher.get("phone_number", "not provided ").lower() == phone.lower():
                    return Response({"error": "teacher new phone number is already used!"},status=status.HTTP_200_OK)


            serializer = TeacherCreateSerializer(teacher, data=request.data, partial=True,context = {"request":request})
            if serializer.is_valid():
                serializer.save()
                # configuring activity log data 
                new_log = ActivityLog.objects.create(
                    school = valid_school,
                    user=request.user,
                    action="UPDATE",
                    module="TEACHER",
                    description=f"{teacher.staff_id} - {teacher.full_name()}"
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
                    "success": "teacher updated successfully",
                    "updated_teacher": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({"error": serializer.errors}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
class TeacherRecordView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_TEACHERS]
    
    def post(self, request,teacher_id):
        try:
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            
             # validate  actions 
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(id=school_id).first()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)

            teacher = Teacher.objects.filter(
                id=teacher_id,
                school_id = school_id
            ).first()
            if not teacher:
                return Response({"error": "Teacher not found "}, status=status.HTTP_200_OK)
            
            # ---------------- Report TEACHER -----------------
            serializer = DisplinaryRecordSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": "Report added successfully",
                        "new_record": serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                    {
                        "error": "Validation failed",
                        "details": serializer.errors
                    },
                    status=status.HTTP_201_CREATED
                )
        except Exception as e :
                return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
    def put(self, request,teacher_id,record_id):
        try:
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            
             # validate director actions 
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            teacher = Teacher.objects.filter(id=school_id,school__id = school_id).prefetch_related(
                "disciplinaryRecords"
            ).first()
            if not teacher :
                return Response({"error": "Invalid  Entry"}, status=status.HTTP_200_OK)

            # ----------------  Upate Report TEACHER -----------------
            record = teacher.disciplinaryRecords.filter(id=record_id).first()
            if not record :
                return Response({"error": "Record not found "}, status=status.HTTP_200_OK)
            serializer = DisplinaryRecordSerializer(record,data=request.data,partial=True)
            if serializer.is_valid() :
                    serializer.save()
                    return Response({
                        "success": f"Report updated successfully",
                        "updated_record": serializer.data
                    }, status=status.HTTP_200_OK)
            return Response({"error": "Record faild!"}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
class TeacherAdministrationView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_TEACHERS]

    def post(self, request,school_id,teacher_id,request_action):
        try:
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
             # validate director actions 
            valid_school = School.objects.filter(id=school_id).first()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)

            teacher = Teacher.objects.filter(
                id=teacher_id,
                school_id=school_id
            ).first()

            if not teacher:
                return Response({"error": "Teacher not found "}, status=status.HTTP_200_OK)
            # ---------------- DELETE TEACHER -----------------
            if request_action == "delete":
                teacher.delete()
                
                # configuring activity log data 
                new_log = ActivityLog.objects.create(
                    school = valid_school,
                    user=request.user,
                    action="DELETE",
                    module="TEACHER",
                    description=f"{teacher.staff_id} - {teacher.full_name()}"
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
                    "success": f"Teacher {request_action} successfully",
                    "del_teacher": {'id':teacher_id}
                }, status=status.HTTP_200_OK)
                
            # ---------------- SUSPEND / ACTIVATE  STUDENT -----------------
            if request_action == "suspend":
                user = teacher.user
                user.is_active = not user.is_active
                user.save()
                request_action = "Activated" if user.is_active else "Suspended" 
                
                 # configuring activity log data 
                new_log = ActivityLog.objects.create(
                    school = valid_school,
                    user=request.user,
                    action="UPDATE",
                    module="TEACHER",
                    description=f"{request_action}. {teacher.staff_id} - {teacher.full_name()}"
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
                    "success": f"Teacher {request_action} successfully",
                    "sus_teacher": {"id":teacher_id,'is_active':user.is_active}
                }, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
 