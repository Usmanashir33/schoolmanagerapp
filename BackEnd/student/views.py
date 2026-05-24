
from django.db.models import Q
from core.formatters import format_serializer_errors
# from core.permissions import DirectorUserPermission
from school.permissions import HasSchoolPermission,SchoolPermissions

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser

from school.tasks import SchoolServices
from .serializers import StudentSerializer,StudentDetailSerializer,StudentCreateSerializer

from core.custom_pegination import CustomPagination50
from .models import Student
from school.models import ActivityLog, School
from authUser.models import User
from school.serializers import ActivityLogSerializer
from django.core.cache import cache
from django.utils import timezone


#==================================================================================================            
#                                       STUDENT SECTION                           
#==================================================================================================
class AllStudentsView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_VIEW_STUDENTS]

    def get(self, request, school_id):
        try:
             # validate director actions
            #  calculate starting minutes to measure speed improvenment 
            start= timezone.now()
            valid_school = School.objects.filter(id=school_id).first()

            if not valid_school:
                return Response(
                    {"error": "Invalid Request"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            page = request.query_params.get("page", 1)
            cache_key = f"students_{school_id}_page_{page}"
            cached_response = cache.get(cache_key)
            if cached_response:
                end = timezone.now()
                # print(f"Cache hit for {cache_key}: {end - start}")
                return Response(cached_response, status=status.HTTP_200_OK)

            students = (
                Student.objects
                .filter(school_id=valid_school.id)
                .select_related(
                    "user",
                    "guardian"
                )
                .prefetch_related(
                    "class_rooms",
                    "class_rooms__class_room"
                )
                .order_by("joined_at")
            ) 

            paginator = CustomPagination50()

            paginated_students = paginator.paginate_queryset(
                students,
                request
            )

            serializer = StudentDetailSerializer(
                paginated_students,
                many=True
            ).data

            resp=paginator.get_paginated_response({
                "success": "School students", 
                "paginated_data": serializer
            })
            cache.set(cache_key,resp,timeout=60*5) # Cache for 5 minutes)
            end = timezone.now()
            # print(f"Cache miss for {cache_key}: {end - start}")
            return Response(resp, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_200_OK
            )
class FilterStudentDetailView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [
        SchoolPermissions.CAN_VIEW_STUDENTS
    ]
    
    # ---------------- GET STUDENT -----------------
    def get(self, request,school_id,searchQuery):  
        try:
            valid_student  = Student.objects.filter(school__id = school_id).filter(
                Q(first_name__icontains = searchQuery) | Q(admission_number__icontains = searchQuery) |
                Q(last_name__icontains = searchQuery)  | Q(middle_name__icontains = searchQuery) | Q(email__icontains = searchQuery) 
            )[:5]
            
            if not valid_student:
                return Response({"success": "not found"}, status=status.HTTP_200_OK)
            serializer = StudentDetailSerializer(valid_student,many=True)
            return Response({
                    "success": "searchResults",
                    "results": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
class StudentDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [HasSchoolPermission]
    required_permissions = [
        SchoolPermissions.CAN_VIEW_STUDENTS,
        SchoolPermissions.CAN_MANAGE_STUDENTS,
        SchoolPermissions.CAN_ADD_STUDENTS,
    ]
    
    # ---------------- GET STUDENT -----------------
    def get(self, request,school_id,student_id):  
        try: 
            # validate director actions 
            valid_student  = Student.objects.filter(id = student_id,school_id=school_id).first()  #.exists()
            if not valid_student:
                return Response({"error": "Student not found"}, status=status.HTTP_200_OK)
            serializer = StudentDetailSerializer(valid_student)
            return Response({
                    "success": "Student details",
                    "student": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK )
            
    def post(self, request):   ## add new student 
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get("school") 
            email = request.data.get("email",'unknown')
            phone = request.data.get("phone",'unknown')
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
             # validate director actions 
            valid_school = School.objects.filter(id=school_id).exists() #.exists()
            if not valid_school:
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)
            
            existed_student = User.objects.filter(
                Q(email__iexact = email) | 
                Q(phone_number__iexact=phone)
                ).values(
                    "email",
                    "phone_number"
                ).first()

            if existed_student:
                if existed_student.get("email", "not provided").lower() == email.lower():
                    return Response({"error": "student email is already used!"},status=status.HTTP_200_OK)
                
                if existed_student.get("phone_number", "not provided ").lower() == phone.lower():
                    return Response({"error": "student phone number is already used!"},status=status.HTTP_200_OK)

            serializer = StudentCreateSerializer(data=request.data,context={"request":request}) 
            if serializer.is_valid():
                serializer.save() 
                return Response({
                    "success": "Student created successfully",
                    "new_student": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({"error": format_serializer_errors(serializer.errors) }, status=status.HTTP_200_OK)

        except Exception as e :
            return Response({"error": str(e) }, status=status.HTTP_200_OK)

    # ---------------- UPDATE STUDENT -----------------
    def put(self, request,student_id):
        try : 
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
             # validate director actions 
            valid_school = School.objects.filter(id=school_id).exists() #.exists()
            if not valid_school:
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)

            student = Student.objects.filter(
                id=student_id, school_id=school_id
            ).first()
            if not student:
                return Response({"error": "Student not found"}, status=status.HTTP_200_OK)
            
            existed_student = Student.objects.filter(
                Q(email=request.data.get("email",'NotFound')) | 
                Q(phone=request.data.get("phone",'NotFound')) 
                ).exclude(id=student_id).values('email','phone').first()
            
            if existed_student and existed_student.get("email",'NotFound').lower() == request.data.get("email").lower() :
                return Response({"error": "email already exists"}, status=status.HTTP_200_OK)
            if existed_student and existed_student.get("phone",'NotFound') == request.data.get("phone") :
                return Response({"error": "phone number already exists"}, status=status.HTTP_200_OK)
             # create student

            serializer = StudentCreateSerializer(student, data=request.data, partial=True, context={"request":request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": "Student updated successfully",
                    "updated_student": serializer.data
                }, status=status.HTTP_200_OK)

            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": str(e) }, status=status.HTTP_200_OK)

class StudentAdministrationView(APIView):
    # parser_classes = [MultiPartParser, FormParser]
    permission_classes = [HasSchoolPermission]
    required_permissions = [
        SchoolPermissions.STUDENTS_MANAGEMENT,
    ]
    
    def post(self, request,student_id,request_action):
        try:
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
             # validate director actions 
            valid_school = School.objects.filter(id=school_id).first() #.exists()
            if not valid_school:
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)

            student = Student.objects.filter(
                id=student_id,
                school_id=school_id
            ).first()

            if not student:
                return Response({"error": "Student not found "}, status=status.HTTP_200_OK)
            serializer = StudentSerializer(student)
            # ---------------- DELETE STUDENT -----------------
            if request_action == "delete":
                student.delete()
                
                # configuring activity log data 
                new_log = ActivityLog.objects.create(
                    school = valid_school,
                    user=request.user,
                    action="DELETE",
                    module="STUDENT",
                    description=f"Student deleted: {student.admission_number} - {student.full_name()}"
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
                    "success": f"Student {request_action} successfully",
                    "del_student": serializer.data
                }, status=status.HTTP_200_OK)
                
            # ---------------- SUSPEND / ACTIVATE  STUDENT -----------------
            if request_action == "suspend":
                user = student.user
                user.is_active = not user.is_active
                user.save()
                request_action = "Activated" if user.is_active else "Suspended" 
                
                # configuring activity log data 
                new_log = ActivityLog.objects.create(
                    school = valid_school,
                    user=request.user,
                    action="UPDATE",
                    module="STUDENT",
                    description=f"Student updated to ({request_action}) : {student.admission_number} - {student.full_name()}"
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
                    "success": f"Student {request_action} successfully",
                    "sus_student": serializer.data
                }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": str(e)}, status=status.HTTP_200_OK)
        
