from functools import partial
# from logging import raiseExceptions
import os ,random,re
from datetime import timedelta
from tabnanny import check

from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken  # or your preferred JWT lib
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q

# core app
# views.py or any view file
from core.emails.email_templates.emails import generate_otp_email,generate_login_email,generate_registration_email
from core.emails.email_templates.emails import generate_school_update_email,generate_school_delete_email
from core.emails.utils.email_service import send_html_email
from core.formatters import format_serializer_errors
from core.permissions import DirectorUserPermission
from core.serializers import SchoolSerializer
from core.utils.otp_generators import generate_5_otp

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from school.models import School ,SchoolDeleteRequest
from authUser.models import User,PendingEmail
from staff.serializers import StaffSerializer,StaffDetailSerializer
from staff.models import Staff
from student.serializers import StudentSerializer,StudentDetailSerializer
from teacher.serializers import TeacherSerializer ,TeacherDetailSerializer
from teacher.models import Teacher 
from subject.serializers import SubjectSerializer
from section.serializers import SchoolSectionDetailSerializer
from section.models import SchoolSection
from classroom.serializers import ClassRoomDetailSerializer
from subject.serializers import SubjectDetailSerializer
from subject.models import Subject


from core.custom_pegination import CustomPagination
from student.models import Student
from classroom.models import ClassRoom
from school.models import School
from student.serializers import StudentSerializer


#==================================================================================================            
#                                       SCHOOL  SECTION                           
#==================================================================================================

class DirectorSchoolDetailView(APIView) :
    parser_classes =[MultiPartParser,FormParser]
    permission_classes=[
        permissions.IsAuthenticated,
        DirectorUserPermission,
    ]
    def get(self, request,school_id): # get school data 
        try:
            school = request.user.director.directorschools.filter(id=school_id).first() # get school and academics
            if not school :
                return Response({"error":"school not found "},status=status.HTTP_200_OK)
            # limited to 100  recordes   
            students = school.students.all().order_by('-joined_at')[:100]
            teachers = school.teachers.all().order_by("-joined_at")[:100]
            staffs = school.staffs.all().order_by('-joined_at')[:100]
            subjects = school.subjects.all().order_by('-added_at')
             
            return Response({
                "success":'school_data', 
                "school_and_academics" : SchoolSerializer(school).data, 
                
                "school_students" : StudentSerializer(students,many=True).data ,
                "school_teachers" : TeacherSerializer(teachers,many=True).data ,
                "school_staffs"   : StaffSerializer(staffs,many=True).data,
                "school_subjects" : SubjectSerializer(subjects,many=True).data,
                }, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK)
        
    
    def put(self, request, school_id) :
        try:
            director = request.user.director
            
            # ============= required fields ==============
            pin = request.data.get('pin')
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            # validate director actions 
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school: 
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
            # make sure unexisted data is not 

            serializer = SchoolSerializer(school, data=request.data, partial=True)
            # authenticate the director 
            # by checking  directord pin 
            if serializer.is_valid() : 
                serializer.save()  
                 # send the email to director
                try:    
                    html_content = generate_school_update_email(
                        school.director.full_name , 
                        school.name, 
                    )
                    send_html_email.delay(
                        subject="School Account Updated" ,
                        to_email=[school.director.email,school.email] , 
                        html_content=html_content
                    )
                except Exception :
                    pass 
                return Response({"success":"school updated successfully", "updated_school": serializer.data}, status=status.HTTP_200_OK)
            return Response({'error': 'Updated data meybe not available change'}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK)
    
    def post(self, request,school_id): # delting the school request 
        try:
            director = request.user.director
            
            # ============= required fields ==============
            pin = request.data.get('pin')
            reason  = request.data.get('reason')
            action = request.data.get("action")
            
            if action != "delete" :
                return Response({"error": "invalid action"}, status=status.HTTP_200_OK)
                
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
             # validate director actions 
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school:
                return Response({"error": "school not Found"}, status=status.HTTP_200_OK)
            
            # craete delte request here 
            if school.delete_requests :
                school.on_delete_request =True
                school.save()
                return Response({"success": "school delete in progress",
                                 "details" :f"R-{school.delete_requests.days_remain()}" }, status=status.HTTP_200_OK) 
            del_request = SchoolDeleteRequest.objects.create( 
                reason = reason, school = school
            )
            del_request.save() 
            # send the email to director
            try:    
                html_content = generate_school_delete_email(
                    school.director.full_name,
                    school.name,
                )
                send_html_email.delay(
                    subject="❌ School Account Deleted",
                    to_email=[school.director.email,school.email],
                    html_content=html_content)
            except: 
                pass
            return Response({"success":"school delete request submitted successfully",'school': SchoolSerializer(school).data},status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
        
        
#==================================================================================================            
#                                       STUDENT SECTION                           
#==================================================================================================
class DirectorAllStudentsView(APIView): #paginated request
    permission_classes = [DirectorUserPermission]
    
    # ---------------- GET  ALL STUDENT -----------------
    def get(self, request,school_id):  
        try:
            director = request.user.director
            # validate director actions 
            valid_school  = School.objects.filter(id = school_id, director=director.id).first()  
            if not valid_school:
                return Response({"error": "Students not found"}, status=status.HTTP_200_OK)
            # get all students 
            students = valid_school.students.all().order_by('joined_at') # all school students 
            paginator = CustomPagination()
            paginated_students = paginator.paginate_queryset(students, request)
            serializer_data = StudentSerializer(students, many=True).data
            paginated_students = paginator.get_paginated_response(serializer_data)
            
            return Response({ 
                    "success": "School students",
                    "students_data": paginated_students.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
class DirectorStudentDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [DirectorUserPermission]
    
    # ---------------- GET STUDENT -----------------
    def get(self, request,student_id):  
        try:
            director = request.user.director
             # validate director actions 
            valid_student  = Student.objects.filter(id = student_id, school__director=director.id).first()  #.exists()
            if not valid_student:
                return Response({"error": "Student not found"}, status=status.HTTP_200_OK)
            serializer = StudentDetailSerializer(valid_student)
            return Response({
                    "success": "Student details",
                    "student": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
            
    def post(self, request):   ## add new student 
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

            serializer = StudentDetailSerializer(data=request.data,context={"request":request}) 
            if serializer.is_valid():
                serializer.save() 
                return Response({
                    "success": "Student created successfully",
                    "new_student": serializer.data
                }, status=status.HTTP_200_OK)
            print("serializer",format_serializer_errors(serializer.errors))
            return Response({"error": format_serializer_errors(serializer.errors) }, status=status.HTTP_200_OK)

        except Exception as e :
            return Response({"error": str(e) }, status=status.HTTP_200_OK)

    # ---------------- UPDATE STUDENT -----------------
    def put(self, request,student_id):
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

            student = Student.objects.filter(
                id=student_id, school__director=director.id
            ).first()
            if not student:
                return Response({"error": "Student not found"}, status=status.HTTP_200_OK)

            serializer = StudentDetailSerializer(student, data=request.data, partial=True, context={"request":request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": "Student updated successfully",
                    "updated_student": serializer.data
                }, status=status.HTTP_200_OK)

            print('serializer.errors: ', format_serializer_errors(serializer.errors))
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": str(e) }, status=status.HTTP_200_OK)

class DirectorStudentAdministrationView(APIView):
    permission_classes = [DirectorUserPermission]
    
    def post(self, request,student_id):
        try:
            director = request.user.director
            pin = request.data.get("pin")
            request_action = request.data.get("action")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)

            student = Student.objects.filter(
                id=student_id,
                school__director=director.id
            ).first()

            if not student:
                return Response({"error": "Student not found "}, status=status.HTTP_200_OK)
            serializer = StudentSerializer(student).data
            
            # ---------------- DELETE STUDENT -----------------
            if request_action == "delete":
                student.delete()
                
            return Response({
                "success": f"Student {request_action} successfully",
                "student": serializer
            }, status=status.HTTP_200_OK)

        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
        
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
            paginator = CustomPagination()
            teachers = paginator.paginate_queryset(teachers, request )
            serializer_data = TeacherSerializer(teachers, many=True).data
            paginated_students = paginator.get_paginated_response(serializer_data)
            
            return Response({ 
                    "success": "School teachers",
                    "teacherss_data": paginated_students.data
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
            # class_room_ids = request.data.get("class_room")
            
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

class DirectorTeacherAdministrationView(APIView):
    permission_classes = [DirectorUserPermission]
    
    def post(self, request,teacher_id):
        try:
            director = request.user.director
            pin = request.data.get("pin")
            request_action = request.data.get("action")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)

            teacher = Teacher.objects.filter(
                id=teacher_id,
                school__director=director.id
            ).first()
            if not teacher:
                return Response({"error": "teacher not found "}, status=status.HTTP_200_OK)
            serializer = TeacherSerializer(teacher).data
            
            # ---------------- DELETE teacher -----------------
            if request_action == "delete":
                teacher.delete()
            return Response({
                "success": f"teacher {request_action} successfully",
                "teacher": serializer
            }, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK) 
        
        
#==================================================================================================            
#                                       STAFF SECTION                           
#==================================================================================================
class DirectorAllStaffsView(APIView): #paginated request
    permission_classes = [DirectorUserPermission]
    # ---------------- GET  ALL Staff -----------------
    def get(self, request,school_id):  
        try:
            director = request.user.director 
            # validate director actions 
            valid_school  = School.objects.filter(id = school_id, director=director.id).first() 
            if not valid_school:
                return Response({"error": "Staff not found"}, status=status.HTTP_200_OK)
            # get all students 
            staffs = valid_school.staffs.all().order_by('joined_at') # all school students 
            paginator = CustomPagination()
            staffs = paginator.paginate_queryset(staffs, request )
            serializer_data = StaffSerializer(staffs, many=True).data
            paginated_staffs = paginator.get_paginated_response(serializer_data)
            
            return Response({ 
                    "success": "School staffs",
                    "staffs_data": paginated_staffs.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
class DirectorStaffView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [DirectorUserPermission]
    # ---------------- GET Staff -----------------
    def get(self, request,staff_id):  
        try:
            director = request.user.director
             # validate director actions 
            valid_staff  = Staff.objects.filter(id = staff_id, school__director=director.id).first()  #.exists()
            if not valid_staff:
                return Response({"error": "staff not found"}, status=status.HTTP_200_OK)
            serializer = StaffSerializer(valid_staff)
            return Response({
                    "success": "staff details",
                    "staff": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
            
    def post(self, request):   ## add new staff 
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

            serializer = StaffDetailSerializer(data=request.data,context = {"request":request}) 
            if serializer.is_valid():
                serializer.save() 
                
                
                return Response({
                    "success": "staff created successfully",
                    "new_staff": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

    # ---------------- UPDATE staff -----------------
    def put(self, request,staff_id):
        try : 
            director = request.user.director
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            # class_room_ids = request.data.get("class_room")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
             # validate director actions 
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)

            staff = Staff.objects.filter(
                id=staff_id, school__director=director.id
            ).first()
            if not staff:
                return Response({"error": "staff not found"}, status=status.HTTP_200_OK)

            serializer = StaffDetailSerializer(staff, data=request.data,partial=True,context = {"request":request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": "staff updated successfully",
                    "updated_staff": serializer.data
                }, status=status.HTTP_200_OK)
            print('serializer.errors: ', serializer.errors)
            return Response({"error": serializer.errors}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

class DirectorStaffAdministrationView(APIView):
    permission_classes = [DirectorUserPermission]
    
    def post(self, request,staff_id):
        try:
            director = request.user.director
            pin = request.data.get("pin") 
            request_action = request.data.get("action")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)

            staff = Staff.objects.filter(
                id=staff_id,
                school__director=director.id
            ).first()
            if not staff:
                return Response({"error": "staff not found "}, status=status.HTTP_200_OK)
            serializer = StaffSerializer(staff).data
            
            # ---------------- DELETE staff -----------------
            if request_action == "delete":
                staff.delete()
            return Response({
                "success": f"staff {request_action} successfully",
                "staff": serializer
            }, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK) 
class DirectorAcademicView(APIView):
    permission_classes = [DirectorUserPermission]
    
    def post(self, request,academic_item):   ## add new staff 
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            
            director = request.user.director
            
             #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
             #--------------- end  validate director actions -------------------
            
            #---------------------------SECTION CREATION -------------------
            if academic_item == "sections":
                # validate section 
                name = request.data.get('name')
                section_found = School.objects.filter(sections__name = name, id=school_id)
                if section_found :
                    return Response({"error": "Name Exist"}, status=status.HTTP_200_OK)
                serializer = SchoolSectionDetailSerializer(data=request.data)
                if serializer.is_valid() :
                    serializer.save()
                    return Response({
                    "success": "Section created successfully",
                    "new_section": serializer.data
                }, status=status.HTTP_200_OK)
                return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
                    
            #---------------------------CLASSROOM CREATION -------------------
            if academic_item == "classrooms":
                # validate section 
                name = request.data.get('name')
                classroom_found = School.objects.filter(sections__classrooms__name = name, id=school_id)
                if classroom_found :
                    return Response({"error": "Name already exist"}, status=status.HTTP_200_OK)
                serializer = ClassRoomDetailSerializer(data=request.data)
                
                if serializer.is_valid() :
                    serializer.save()
                    return Response({
                    "success": "Class Room created successfully",
                    "new_classroom": serializer.data
                }, status=status.HTTP_200_OK)
                return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
            
            #---------------------------SUBJECTS CREATION -------------------
            if academic_item == "subjects":
                # validate section 
                name = request.data.get('name')
                code = request.data.get('code')
                subject_found = School.objects.filter(
                    Q(subjects__name__iexact=name) | Q(subjects__code__iexact=code),
                    id=school_id
                ).exists()

                if subject_found:
                    return Response(
                        {"error": "Subject name or code already exists"},
                        status=status.HTTP_200_OK
                    )
                serializer = SubjectDetailSerializer(data=request.data,context = {"request":request})
                if serializer.is_valid() :
                    serializer.save()
                    return Response({
                    "success": "Subject added successfully",
                    "new_subject": serializer.data
                }, status=status.HTTP_200_OK)
                return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
    def put(self, request,academic_item,item_id):   ## update  
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            director = request.user.director
             #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
             #--------------- end  validate director actions -------------------
            
            #---------------------------SECTION UPDATE -------------------
            if academic_item == "sections":
                # validate section 
                name = request.data.get('name')
                name_exist = SchoolSection.objects.filter(
                    school=school_id,
                    name=name
                ).exclude(
                    id=item_id
                )
                if name_exist :
                    return Response({"error": "Section name alraedy exist"}, status=status.HTTP_200_OK)
                section = SchoolSection.objects.filter(id = item_id).first()
                if not section :
                    return Response({"error": "Section not exist"}, status=status.HTTP_200_OK)
                    
                serializer = SchoolSectionDetailSerializer(section, data=request.data,partial=True)
                if serializer.is_valid() :
                    serializer.save()
                    return Response({
                    "success": "Section update successfully",
                    "updated_section": serializer.data
                }, status=status.HTTP_200_OK)
                return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
                    
            #---------------------------CLASSROOM UPDATE -------------------
            if academic_item == "classrooms":
                # validate section 
                name = request.data.get('name')
                name_exist = ClassRoom.objects.filter(
                    name=name
                ).exclude(
                    id=item_id
                )
                if name_exist :
                    return Response({"error": "Section name alraedy exist"}, status=status.HTTP_200_OK)
                classroom = ClassRoom.objects.filter(id = item_id).first()
                if not classroom :
                    return Response({"error": "Class not exist"}, status=status.HTTP_200_OK)
                
                serializer = ClassRoomDetailSerializer(classroom,data=request.data,partial=True)
                if serializer.is_valid() :
                    serializer.save()
                    return Response({
                    "success": "Classroom updated successfully",
                    "updated_classroom": serializer.data 
                }, status=status.HTTP_200_OK)
                return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
            
            #---------------------------SUBJECTS UPDATE-------------------
            if academic_item == "subjects":
                # validate section 
                name = request.data.get('name')
                code = request.data.get('code')
                
                
                subject_exists = Subject.objects.filter(
                        school_id=school_id
                    ).filter(
                        Q(name__iexact=name) | Q(code__iexact=code)
                    ).exclude(
                        id=item_id
                    ).exists()

                if subject_exists:
                    return Response(
                        {"error": "Subject name or code already exists"},
                        status=status.HTTP_200_OK
                    )
                subject = Subject.objects.filter(id = item_id).first()
                if not subject:
                    return Response(
                        {"error": "Subject not  exists"},
                        status=status.HTTP_200_OK
                    )
                
                serializer = SubjectDetailSerializer(subject,data=request.data,partial=True)
                if serializer.is_valid() :
                    serializer.save()
                    return Response({
                    "success": "Subject Updated successfully",
                    "updated_subject": serializer.data
                }, status=status.HTTP_200_OK)
                return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
