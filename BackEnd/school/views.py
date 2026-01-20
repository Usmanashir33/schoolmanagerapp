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
from urllib3 import request

# core app
# views.py or any view file
from core.emails.email_templates.emails import generate_otp_email,generate_login_email,generate_registration_email
from core.emails.email_templates.emails import generate_school_update_email,generate_school_delete_email
from core.emails.utils.email_service import send_html_email
from core.permissions import DirectorUserPermission

from core.serializers import SchoolSerializer,DirectorSerializer
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from .models import  School ,SchoolDeleteRequest
from director.models import Director 
from authUser.models import User,PendingEmail
from core.utils.otp_generators import generate_5_otp
 


# we need directors verifed email to ctreat a school 
# it requires otp verification for second step
class SchoolAndDirectorCreateView(APIView) :
    parser_classes =[MultiPartParser,FormParser]
    permission_classes=[permissions.AllowAny]
    def post(self, request):
        try:
            # check if otp request 
            verification_code = request.data.get('otp')
            email = request.data.get('school_email')
            name = request.data.get('school_name')
            tag = request.data.get('school_tag')
            phone = request.data.get('school_phone')
            address = request.data.get('school_address')
            
            # director details
            director_title = request.data.get('director_title')
            director_first_name = request.data.get('director_first_name')
            director_last_name = request.data.get('director_last_name')
            director_middle_name = request.data.get('director_middle_name')
            director_email = request.data.get('director_email')
            director_phone = request.data.get('director_phone')
            director_gender = request.data.get('director_gender')
            
            
            director_password = request.data.get('director_password')
            director_password2 = request.data.get('director_password2')

            # check if school or director email is used ame o email
            if School.objects.filter( email__iexact=email ).exists() :
                return Response({"error":"school email already used!"},status=status.HTTP_200_OK)
            
            if Director.objects.filter( email__iexact=director_email ).exists() :
                return Response({"error":"director email already used!"},status=status.HTTP_200_OK)
            if Director.objects.filter( phone__iexact=phone ).exists() :
                return Response({"error":"director phone already used!"},status=status.HTTP_200_OK)
            
            if School.objects.filter( phone__iexact=phone ).exists() :
                return Response({"error":"school phone already used!"},status=status.HTTP_200_OK)
            
            if School.objects.filter( tag__iexact=tag ).exists():
                return Response({"error":"school tag already used!"},status=status.HTTP_200_OK)
            
            if School.objects.filter( name__iexact=name ).exists():
                return Response({"error":"school name already used!"},status=status.HTTP_200_OK)
            
            # check paswords match - and greater than 7 
            if not director_password == director_password2 :
                return Response({"error":"director password required"},status=status.HTTP_200_OK)
            if len(director_password) < 7 :
                return Response({"error":"director password too short"},status=status.HTTP_200_OK)
            
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
                        subject="🔐 Your Director OTP Code 10Min ",
                        to_email=director_email,
                        html_content=html_content
                    )
                except :
                    pass
                return Response({"success":"otp_sent",},status=status.HTTP_200_OK) 
            
            #-------------- with otp check the OTP and create new school--------------------
             
            # validate verification_code 
            pending_email = PendingEmail.objects.filter(email = director_email)
            
            if not pending_email.exists() :
                return Response({"error":"email not registered "},status=status.HTTP_200_OK)
            
            #pending email exists continue processing 
            found_email = pending_email.first()
            if found_email.is_expired() :
                found_email.delete()
                return Response({"error":"expired! school not registered"},status=status.HTTP_200_OK)
            if not found_email.checkCode(verification_code) :
                return Response({"error":"invalid  verification code"},status=status.HTTP_200_OK)
            
            # every thing is ohk # create school  and director user
            new_director = DirectorSerializer( data={
                'first_name': director_first_name,
                'last_name': director_last_name,
                'middle_name': director_middle_name,
                'email': director_email,
                'phone': director_phone,
                'title':director_title,
                'gender':director_gender,
                'role':'Director',
            })
            serializer = SchoolSerializer(data={
                'name': name,       
                'tag': tag,
                'phone': phone,
                'address': address,
                'email': email,
            })
            if serializer.is_valid() and new_director.is_valid() :   
            #   create school here and director user
                director = new_director.save()
                director.user.set_password(director_password)
                director.user.email_verified = True  
                director.user.save()
                
                school = serializer.save()
                school.director = director
                school.save()
                
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
                    "data": DirectorSerializer(director).data   
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