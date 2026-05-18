from django.db.models import Q

# core app
# views.py or any view file
from core.formatters import format_serializer_errors
from core.permissions import DirectorUserPermission

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from teacher.serializers import TeacherSerializer ,TeacherDetailSerializer,DisplinaryRecordSerializer
from teacher.models import Teacher 

from core.custom_pegination import CustomPagination50
from school.models import School


#==================================================================================================            
#                                       TEACHER SECTION                           
#==================================================================================================
class DirectorAllTeachersView(APIView): #paginated request
    permission_classes = [DirectorUserPermission]
    
    # ---------------- GET  ALL Teachers -----------------
    def get(self, request,school_id):  
        try:
            director = request.user.director
            # validate director actions 
            valid_school  = School.objects.filter(id = school_id, director=director.id).first() 
            if not valid_school:
                return Response({"error": "Teachers not found"}, status=status.HTTP_200_OK)
            # get all students 
            teachers = valid_school.teachers.all().order_by('joined_at') # all school students 
            paginator = CustomPagination50()
            teachers = paginator.paginate_queryset(teachers, request )
            serializer_data = TeacherSerializer(teachers, many=True).data
            paginated_students = paginator.get_paginated_response(serializer_data)
            
            return Response({ 
                    "success": "School teachers",
                    "teacherss_data": paginated_students.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
class DirectorFilterTeacherDetailView(APIView):
    permission_classes = [DirectorUserPermission]
    # ---------------- SERCH Teacher -----------------
    def get(self, request,searchQuery):  
        try:
            director = request.user.director
             # validate director actions 
            searched  = Teacher.objects.filter(
                Q(id__icontains = searchQuery)  | Q(first_name__icontains = searchQuery) |  Q(title__icontains = searchQuery) |
                Q(last_name__icontains = searchQuery)  | Q(middle_name__icontains = searchQuery) | Q(email__icontains = searchQuery) |
                  Q(phone__icontains = searchQuery) | Q(staff_id__icontains = searchQuery)
            ).filter(school__director__id = director.id)
            
            if not searched:
                return Response({"success": "not found"}, status=status.HTTP_200_OK)
            serializer = TeacherDetailSerializer(searched,many=True)
            return Response({
                    "success": "searchResults",
                    "results": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

class DirectorTeacherDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [DirectorUserPermission]
    # ---------------- GET Teacher -----------------
    def get(self, request,teacher_id):  
        try:
            director = request.user.director
             # validate director actions 
            valid_teacher  = Teacher.objects.filter(id = teacher_id, school__director=director.id).first()  #.exists()
            if not valid_teacher:
                return Response({"error": "Teacher not found"}, status=status.HTTP_200_OK)
            serializer = TeacherSerializer(valid_teacher)
            return Response({
                    "success": "teacher details",
                    "teacher": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
            
    def post(self, request):   ## add new teacher 
        try:
            director = request.user.director
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
             # validate director actions 
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)

            serializer = TeacherDetailSerializer(data=request.data,context = {"request":request}) 
            if serializer.is_valid():
                serializer.save() 
                
                return Response({
                    "success": "Teacher created successfully",
                    "new_teacher": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)

        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

    # ---------------- UPDATE TEACHER -----------------
    def put(self, request,teacher_id):
        try : 
            director = request.user.director
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
             # validate director actions 
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)

            teacher = Teacher.objects.filter(
                id=teacher_id, school__director=director.id
            ).first()
            if not teacher:
                return Response({"error": "teacher not found"}, status=status.HTTP_200_OK)

            serializer = TeacherDetailSerializer(teacher, data=request.data, partial=True,context = {"request":request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": "teacher updated successfully",
                    "updated_teacher": serializer.data
                }, status=status.HTTP_200_OK)
            print('serializer.errors: ', serializer.errors)
            return Response({"error": serializer.errors}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

from teacher.models import DisplinaryRecord
class DirectorTeacherRecordView(APIView):
    permission_classes = [DirectorUserPermission]
    def post(self, request,teacher_id):
        try:
            director = request.user.director
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            
             # validate director actions 
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)

            teacher = Teacher.objects.filter(
                id=teacher_id,
                school__director=director.id
            ).first()
            if not teacher:
                return Response({"error": "Teacher not found "}, status=status.HTTP_200_OK)
            
            # ---------------- Report TEACHER -----------------
            serializer = DisplinaryRecordSerializer(data=request.data)
            print('serializer: ', serializer)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": "Report added successfully",
                        "new_report": serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )

            return Response(
                    {
                        "error": "Validation failed",
                        "details": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e :
                return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
    def put(self, request,teacher_id,record_id):
        try:
            director = request.user.director
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            
             # validate director actions 
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)

            # ----------------  Upate Report TEACHER -----------------
            record = DisplinaryRecord.objects.filter(id=record_id,teacher=teacher_id)
            if not record :
                return Response({"error": "Record not found "}, status=status.HTTP_200_OK)
            serializer = DisplinaryRecordSerializer(record,data=request.data,partial=True)
            if serializer.is_valid() :
                    serializer.save()
                    return Response({
                        "success": f"Report updated successfully",
                        "updated_report": serializer.data
                    }, status=status.HTTP_200_OK)
            return Response({"error": "Record faild!"}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
class DirectorTeacherAdministrationView(APIView):
    permission_classes = [DirectorUserPermission]
    def post(self, request,teacher_id,request_action):
        try:
            director = request.user.director
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            print('school_id: ', school_id)
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
             # validate director actions 
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)

            teacher = Teacher.objects.filter(
                id=teacher_id,
                school__director=director.id
            ).first()

            if not teacher:
                return Response({"error": "Teacher not found "}, status=status.HTTP_200_OK)
            serializer = TeacherSerializer(teacher)
            # ---------------- DELETE TEACHER -----------------
            if request_action == "delete":
                teacher.delete()
                return Response({
                    "success": f"Teacher {request_action} successfully",
                    "del_teacher": serializer.data
                }, status=status.HTTP_200_OK)
            # ---------------- SUSPEND / ACTIVATE  STUDENT -----------------
            if request_action == "suspend":
                user = teacher.user
                user.is_active = not user.is_active
                user.save()
                request_action = "Activated" if user.is_active else "Suspended" 
                return Response({
                    "success": f"Teacher {request_action} successfully",
                    "sus_teacher": serializer.data
                }, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
