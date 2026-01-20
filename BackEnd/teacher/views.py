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

from .serializers import SchoolSerializer,TeacherSerializer
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from .models import School ,Teacher 
from authUser.models import User,PendingEmail
from core.utils.otp_generators import generate_5_otp



# we need directors verifed email to ctreat a school 
class DirectorTeacherView(APIView) :
    parser_classes =[MultiPartParser,FormParser]
    permission_classes=[DirectorUserPermission]
    def post(self, request): #add new Teacher 
        try:
            pin = request.data.get('pin')
            email = request.data.get('email').lower()
            verified = request.user.userspin.checkPin(pin) 
            if not verified :
                return Response({"error":'user pins error'},status=status.HTTP_200_OK)
            # verify no user with that email 
            if Teacher.objects.filter(email__iexact = email).exists() :
                return Response({"error":"email exist"},status=status.HTTP_200_OK)
            school = School.objects.filter(id=request.data.get('school'))
            if not school.exists():
                return Response({"error":"school not found"},status=status.HTTP_200_OK)
            
            serializer = TeacherSerializer(data = request.data)
            if serializer.is_valid() :
                serializer.save()
                # send email to teacher and school 
                try:    
                    html_content = generate_school_update_email(
                        serializer.email,
                        school.name,
                    )
                    send_html_email.delay(
                        subject="School Teacher Craeted",
                        to_email=[serializer.email,school.email],
                        html_content=html_content 
                    )
                except:
                    pass
                return Response({"success":"Teacher Created","teacher":serializer.data},status=status.HTTP_200_OK)
            return Response({"error":"server error"},status=status.HTTP_200_OK)
        except :
           return Response({"error":"server error"},status=status.HTTP_200_OK)
    
    def put(self, request):  # upadte Teacher by director 
        try:
            teacher_id = request.data.get('school_id')
            pin = request.data.get('pin')
            
            verified = request.user.userspin.checkPin(pin) 
            if not verified :
                return Response({"error":'user pins error'},status=status.HTTP_200_OK)
            
            teacher = get_object_or_404(Teacher, id=teacher_id, school__director=request.user)
            serializer = SchoolSerializer(teacher, data=request.data, partial=True)
            # authenticate the director 
            # by checking  directord pin 
            if serializer.is_valid() : 
                serializer.save() 
            pass
        except :
           return Response({"error":"server error"},status=status.HTTP_200_OK)
       
# the view mainly for teachers 
class TeacherSelfView(APIView) : 
    parser_classes =[MultiPartParser,FormParser]
    # permission_classes=[DirectorUserPermission]
    def get(self, request): #add new Teacher
        try:
            teacher = Teacher.objects.filter(id = request.user.teacher.id).first() 
            serializer = TeacherSerializer(teacher)
            return Response({"success":"success","teacher":serializer.data},status=status.HTTP_200_OK)
        except :
           return Response({"error":"server error"},status=status.HTTP_200_OK)
    
    def put(self, request): #add new Teacher 
        try:
            pin = request.data.get('pin')
            email = request.data.get('email').lower()
            phone = request.data.get('phone')
            verified = request.user.userspin.checkPin(pin)
            
            if not verified :
                return Response({"error":'user pins error'},status=status.HTTP_200_OK)
            
            # verify no user with that email 
            if User.objects.filter(email__iexact = email).exists() :
                return Response({"error":"email exist"},status=status.HTTP_200_OK)
            if User.objects.filter(phone_number__iexact = phone).exists() :
                return Response({"error":"phone exist"},status=status.HTTP_200_OK)
            teacher = get_object_or_404(Teacher, user = request.user)
            serializer = TeacherSerializer(teacher, data=request.data, partial=True)
            if serializer.is_valid() :
                serializer.save()
                # send email to teacher and school 
                try:    
                    html_content = generate_teacher_update_email(
                        f"{teacher.user.first_name} {teacher.user.last_name}",
                        teacher.school.name
                    )
                    send_html_email.delay(
                        subject="School Profile Updated",
                        to_email=[teacher.user.email],
                        html_content=html_content
                    )
                except:
                    pass
                return Response({"success":"Profile Updated","teacher":serializer.data},status=status.HTTP_200_OK)
            return Response({"error":"server error"},status=status.HTTP_200_OK)
        except :
           return Response({"error":"server error"},status=status.HTTP_200_OK)