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
from core.emails.email_templates.emails import generate_otp_email,generate_login_email,generate_registration_email
from core.emails.email_templates.emails import generate_school_update_email,generate_school_delete_email
from core.emails.utils.email_service import send_html_email
from core.permissions import DirectorUserPermission

from .serializers import SchoolSerializer
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from .models import School ,SchoolDeleteRequest
from authUser.models import User,PendingEmail
from core.utils.otp_generators import generate_5_otp



# we need directors verifed email to ctreat a school 
class SchoolCreateView(APIView) :
    parser_classes =[MultiPartParser,FormParser]
    permission_classes=[permissions.AllowAny]
    def post(self, request):
        try:
            # check if otp request 
            verification_code = request.data.get('verification_code')
            director_email = request.data.get('director_email').lower()
            email = request.data.get('email').lower()
            name = request.data.get('name').lower()
            tag = request.data.get('tag').lower()
            phone = request.data.get('phone').lower()
            
            # check if director email is used ame o email
            if School.objects.filter( email__iexact=email ).exists() :
                return Response({"error":"school email already used"},status=status.HTTP_200_OK)
            
            if School.objects.filter( phone__iexact=phone ).exists() :
                return Response({"error":"school phone already used"},status=status.HTTP_200_OK)
            
            if School.objects.filter( tag__iexact=tag ).exists():
                return Response({"error":"school tag already used"},status=status.HTTP_200_OK)
            
            if School.objects.filter( name__iexact=name ).exists():
                return Response({"error":"school name already used"},status=status.HTTP_200_OK)
            
            if User.objects.filter( email__iexact= director_email).exists():
                return Response({"error":"director email already used"},status=status.HTTP_200_OK)
            
            # check if pending email exist create the pending email verification for director
            # check if its first request we need to send otp
             # check passwords match
            if request.data.get('director_password') != request.data.get('director_password2'):
                return Response({"error":"director passwords do not match"},status=status.HTTP_200_OK)
            
            if not verification_code :# send verification code 
                verification_code_gen = generate_5_otp() 
                
                # set new code and save
                pending_email,created  = PendingEmail.objects.get_or_create(email = director_email)
                pending_email.setCode(verification_code_gen)
                
                print(verification_code_gen,"Generated OTP for",director_email)
                print('pending_email',pending_email)
                #we send email with email_verification_code to directors Email 
                #send email here 
                try:
                    html_content = generate_otp_email(director_email,verification_code_gen )
                    send_html_email.delay(
                        subject="🔐 Your Director OTP Code 15Min ",
                        to_email=director_email,
                        html_content=html_content
                    )
                except :
                    pass
                return Response({"success":"otp_sent",},status=status.HTTP_200_OK) 
            # it comes with otp check the otp and create new school 
            # validate verification_code 
            pending_email = PendingEmail.objects.filter(email = director_email)
            
            if not pending_email.exists() :
                return Response({"error":"email not registered "},status=status.HTTP_200_OK)
            
            found_email = pending_email.first()
            if not found_email.checkCode(verification_code) :
                return Response({"error":"invalid  verification code"},status=status.HTTP_200_OK)
            if found_email.is_expired() :
                return Response({"error":"expired verification code"},status=status.HTTP_200_OK)
            
            # every thing is ohk # create school
            serializer = SchoolSerializer(data=request.data)
            if serializer.is_valid():   
            #   create school not by using serializer
                school = serializer.save()
                school.director_password = make_password(serializer.validated_data.get('director_password'))    
                school.save()
                school.director.set_password(request.data.get('director_password'))
                school.director.save()
                pending_email.delete() # delete pending email after verification
                
                # send success email to director
                try:    
                    html_content = generate_registration_email(
                        director_email,
                        school.director_fullname,
                        school.director_email,
                    )
                    send_html_email.delay(
                        subject="✅ Your Director & School Account Created",
                        to_email=[director_email,school.email],
                        html_content=html_content
                    )
                except:
                    pass
                return Response({
                    "success":"school created successfully",
                    "school": SchoolSerializer(school).data
                    },status=status.HTTP_201_CREATED)
            else :
                print(serializer.errors)
                return Response({"error":"failed to create school "},status=status.HTTP_200_OK)
        except :
           return Response({"error":"server error"},status=status.HTTP_200_OK)
       
# considering the above function craete  another view for update delete and get school details only director of the school can access it.
class DirectorSchoolDetailView(APIView) :
    parser_classes =[MultiPartParser,FormParser]
    permission_classes=[
        permissions.IsAuthenticated,
        DirectorUserPermission,
    ]
    def get(self, request):
        try:
            schools = request.user.directorschools.all()
            serializer = SchoolSerializer(schools,many=True)
            return Response({"success":'success', "schools": serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK)
    
    def put(self, request, ):
        try:
            school_id = request.data.get('school_id')
            pin = request.data.get('pin')
            
            school = get_object_or_404(School, id=school_id, director=request.user)
            serializer = SchoolSerializer(school, data=request.data, partial=True)
            # authenticate the director 
            # by checking  directord pin 
            verified = request.user.userspin.checkPin(pin) 
            if not verified :
                return Response({"error":'user pins error'},status=status.HTTP_200_OK)
            if serializer.is_valid() : 
                serializer.save() 
                 # send the email to director
                try:    
                    html_content = generate_school_update_email(
                        school.director_fullname,
                        school.name,
                    )
                    send_html_email.delay(
                        subject="School Account Updated",
                        to_email=[school.director_email,school.email],
                        html_content=html_content
                    )
                except:
                    pass
                return Response({"success":"school updated successfully", "school": serializer.data}, status=status.HTTP_200_OK)
            return Response({'error': 'invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK)
    
    def post(self, request,): # delting the school request 
        try:
            school_id = request.data.get('school_id')
            pin = request.data.get('pin')
            reason = request.data.get('reason')
            
            school = get_object_or_404(School, id=school_id, director=request.user)
            # authenticate the director # by checking  directord pin 
            verified = request.user.userspin.checkPin(pin) 
            if not verified :
                return Response({"error":'user pins error'},status=status.HTTP_200_OK)
            # craete delte request here 
            del_request = SchoolDeleteRequest.objects.create(
                reason = reason ,
                school = school
            )
            del_request.save()
            # send the email to director
            try:    
                html_content = generate_school_delete_email(
                    school.director_fullname,
                    school.name,
                )
                send_html_email.delay(
                    subject="❌ School Account Deleted",
                    to_email=[school.director_email,school.email],
                    html_content=html_content)
            except: 
                pass
            return Response({"success":"school delete request submitted successfully",'school': SchoolSerializer(school).data},status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 