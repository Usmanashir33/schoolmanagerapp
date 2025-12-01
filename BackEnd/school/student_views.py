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

from .serializers import SchoolSerializer,TeacherSerializer,ClassRoomSerializer
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from .models import School ,SchoolDeleteRequest,Teacher ,SchoolSection,ClassRoom
from authUser.models import User,PendingEmail
from core.utils.otp_generators import generate_5_otp

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from core.permissions import DirectorUserPermission
from .models import Student, ClassRoom
from .serializers import StudentSerializer

class DirectorStudentView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [DirectorUserPermission]

    # ---------------- CREATE STUDENT -----------------
    def post(self, request):
        try:
            pin = request.data.get("pin")
            if not request.user.userspin.checkPin(pin):
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)

            # Validate classroom belongs to director's school
            classroom_id = request.data.get("class_room")
            classroom = ClassRoom.objects.filter(
                id=classroom_id,
                section__school__director=request.user
            ).first()

            if not classroom:
                return Response({"error": "Classroom not found or not yours"}, status=status.HTTP_200_OK)

            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": "Student created successfully",
                    "student": serializer.data
                }, status=status.HTTP_200_OK)

            return Response({"error": serializer.errors}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

    # ---------------- UPDATE STUDENT -----------------
    def put(self, request):
        try:
            pin = request.data.get("pin")
            if not request.user.userspin.checkPin(pin):
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)

            student_id = request.data.get("student_id")
            student = Student.objects.filter(
                id=student_id,
                class_room__section__school__director=request.user
            ).first()

            if not student:
                return Response({"error": "Student not found or not yours"}, status=status.HTTP_200_OK)

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

    # ---------------- DELETE STUDENT -----------------
    def delete(self, request):
        try:
            pin = request.data.get("pin")
            if not request.user.userspin.checkPin(pin):
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)

            student_id = request.data.get("student_id")
            student = Student.objects.filter(
                id=student_id,
                class_room__section__school__director=request.user
            ).first()

            if not student:
                return Response({"error": "Student not found or not yours"}, status=status.HTTP_200_OK)

            serializer = StudentSerializer(student)
            student.delete()
            return Response({
                "success": "Student deleted successfully",
                "student": serializer.data
            }, status=status.HTTP_200_OK)

        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
