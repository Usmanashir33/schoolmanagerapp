from functools import partial
import os, random, re
from datetime import timedelta

from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from core.emails.email_templates.emails import (
    
    generate_school_update_email,
)
from core.emails.utils.email_service import send_html_email
from core.permissions import DirectorUserPermission

from core.serializers import *
from .models import SchoolSection
from authUser.models import User, PendingEmail
from core.utils.otp_generators import generate_5_otp


# ------------------------------------------------------------
#          DIRECTOR CREATE AND UPDATE SECTIONS
# ------------------------------------------------------------

class DirectorSectionView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [DirectorUserPermission]

    # ---------------- CREATE SECTION -----------------
    def post(self, request):
        try:
            # Validate director PIN
            pin = request.data.get('pin')
            if not request.user.userspin.checkPin(pin):
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)

            # Validate School
            school_id = request.data.get('school')
            school = School.objects.filter(id=school_id).first()

            if not school:
                return Response({"error": "School not found"}, status=status.HTTP_200_OK)

            # Serialize and save section
            serializer = SchoolSectionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                # Send email notification
                try:
                    html_content = generate_school_update_email(
                        school.director.first_name,
                        school.name,
                    )
                    send_html_email.delay(
                        subject="New Section Created",
                        to_email=[school.email],
                        html_content=html_content
                    )
                except:
                    pass

                return Response({
                    "success": "New Section added",
                    "section": serializer.data
                }, status=status.HTTP_200_OK)

            return Response({"error": serializer.errors}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

    # ---------------- UPDATE SECTION -----------------
    def put(self, request):
        try:
            # Extract input
            section_id = request.data.get('section_id')
            pin = request.data.get('pin')

            # Verify PIN
            if not request.user.userspin.checkPin(pin):
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)

            # Validate section belongs to director
            section = get_object_or_404(
                SchoolSection,
                id=section_id,
                school__director=request.user
            )

            # Use correct serializer
            serializer = SchoolSectionSerializer(section, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": "Section updated",
                    "section": serializer.data
                }, status=status.HTTP_200_OK)

            return Response({"error": serializer.errors}, status=status.HTTP_200_OK)

        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)


# ------------------------------------------------------------
#             DIRECTOR DELETE SECTION
# ------------------------------------------------------------

class DirectorSectionDeleteView(APIView):
    parser_classes = [MultiPartParser, FormParser] 
    permission_classes = [DirectorUserPermission]

    def post(self, request):
        try:
            section_id = request.data.get('section_id')
            pin = request.data.get('pin')

            # Check pin
            if not request.user.userspin.checkPin(pin):
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)

            # Check if section exists & belongs to director
            section = get_object_or_404(
                SchoolSection,
                id=section_id,
                school__director=request.user
            )

            # Prepare response before deletion
            serializer = SchoolSectionSerializer(section)

            # Delete section
            section.delete()

            return Response({
                "success": "Section deleted",
                "section": serializer.data
            }, status=status.HTTP_200_OK)

        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
