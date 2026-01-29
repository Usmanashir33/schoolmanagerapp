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

# core app
# views.py or any view file
from core.emails.email_templates.emails import generate_teacher_update_email,generate_login_email,generate_registration_email
from core.emails.email_templates.emails import generate_school_update_email,generate_school_delete_email
from core.emails.utils.email_service import send_html_email
from core.permissions import DirectorUserPermission

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from authUser.models import User,PendingEmail
from core.utils.otp_generators import generate_5_otp

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from core.permissions import DirectorUserPermission
from core.custom_pegination import CustomPagination
from .models import Student
from classroom.models import ClassRoom
from school.models import School
from .serializers import StudentSerializer

class DirectorAllStudentsView(APIView):
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
class DirectorStudentView(APIView):
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

            serializer = StudentSerializer(valid_student)
            return Response({
                    "success": "Student details",
                    "student": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
            
    def post(self, request):  
        try:
            director = request.user.director
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            class_room_ids = request.data.get("class_room")
            print('class_room_ids: ', class_room_ids)
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
             # validate director actions 
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)

            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save() 
                if class_room_ids :
                    class_rooms = ClassRoom.objects.filter(id__in=class_room_ids)
                    serializer.instance.class_room.set(class_rooms)
                serializer.save()
                return Response({
                    "success": "Student created successfully",
                    "new_student": serializer.data
                }, status=status.HTTP_200_OK)

            return Response({"error": serializer.errors}, status=status.HTTP_200_OK)

        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

    # ---------------- UPDATE STUDENT -----------------
    def put(self, request,student_id):
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

            student = Student.objects.filter(
                id=student_id, school__director=director.id
            ).first()
            if not student:
                return Response({"error": "Student not found"}, status=status.HTTP_200_OK)

            serializer = StudentSerializer(student, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": "Student updated successfully",
                    "student": serializer.data
                }, status=status.HTTP_200_OK)

            return Response({"error": serializer.errors}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

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