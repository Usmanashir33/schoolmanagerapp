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


class DirectorDeleteClassRoomView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [DirectorUserPermission]
    # ---------------- DELETE CLASSROOM -----------------
    def post(self, request):
        try:
            classroom_id = request.data.get("classroom_id")
            pin = request.data.get("pin")

            # Check PIN
            if not request.user.userspin.checkPin(pin):
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)

            # Validate classroom
            classroom = ClassRoom.objects.filter(
                id=classroom_id,
                section__school__director=request.user
            ).first()

            if not classroom:
                return Response({"error": "Classroom not found"}, status=status.HTTP_200_OK)

            serializer = ClassRoomSerializer(classroom)
            classroom.delete()
            
             # send email to class teacher and school 
            try:    
                    html_content = generate_teacher_update_email(
                        f"{classroom.class_teacher.user.first_name} {classroom.class_teacher.user.last_name}",
                        classroom.school.name
                    )
                    send_html_email.delay(
                        subject="School Class Deleted",
                        to_email=[classroom.class_teacher.user.email],
                        html_content=html_content
                    )
            except:
                pass

            return Response({
                "success": "Classroom deleted successfully",
                "classroom": serializer.data
            }, status=status.HTTP_200_OK)

        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

class DirectorClassRoomView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [DirectorUserPermission]

    # ---------------- CREATE CLASSROOM -----------------
    def post(self, request):
        try:
            # Check director pin
            pin = request.data.get("pin")
            if not request.user.userspin.checkPin(pin):
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)

            # Validate section
            section_id = request.data.get("section")
            section = SchoolSection.objects.filter(
                id=section_id,
                school__director=request.user
            ).first()

            if not section:
                return Response({"error": "Section not found"}, status=status.HTTP_200_OK)

            # Create classroom
            serializer = ClassRoomSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": "Classroom created successfully",
                    "classroom": serializer.data
                }, status=status.HTTP_200_OK)

            return Response({"error": 'class not saved'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

    # ---------------- UPDATE CLASSROOM -----------------
    def put(self, request):
        try:
            classroom_id = request.data.get("classroom_id")
            pin = request.data.get("pin")

            # Check PIN
            if not request.user.userspin.checkPin(pin):
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)

            # Validate classroom belongs to director's school
            classroom = ClassRoom.objects.filter(
                id=classroom_id,
                section__school__director=request.user
            ).first()

            if not classroom:
                return Response({"error": "Classroom not found"}, status=status.HTTP_200_OK)

            serializer = ClassRoomSerializer(
                classroom,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": "Classroom updated successfully",
                    "classroom": serializer.data
                }, status=status.HTTP_200_OK)

            return Response({"error": serializer.errors}, status=status.HTTP_200_OK)

        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

    