from functools import partial
# from logging import raiseExceptions
import os ,random,re
from datetime import timedelta
from tabnanny import check

from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken  # or your preferred JWT lib

# core app
# views.py or any view file
from core.serializers import DirectorSerializer, ParentsSerializer, StudentSerializer, TeacherSerializer,StaffSerializer
from core.emails.email_templates.emails import generate_otp_email,generate_login_email,generate_registration_email
from core.emails.utils.email_service import send_html_email


from .serializers import UserSerializer, MiniUserSerializer
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from .models import User, VerificationCode

# Create your views here.
def create_jwt_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    
def generate_5_otp() :
    code = random.randint(12345,98769)
    return  code 

def serialize_with_role(user,role) -> dict | None :
    if role == "Director" : # director role we will send him director data
        data = DirectorSerializer(user.director).data
    elif role == "Teacher" :
        data = TeacherSerializer(user.teacher).data
    elif user.role == "Staff" :
        data = StaffSerializer(user.staff).data
    elif role == "Student" :
        data = StudentSerializer(user.student).data 
    elif role == "Parent" :
        data = ParentsSerializer(user.parent).data
    else : 
        return None 
    return data

def find_user_by_email_username(input_value) -> User | None:
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'  # Basic email pattern
    # username_regex = r'^[a-zA-Z0-9/]+$'
    
    if re.match(email_regex, input_value.lower()): # director or parent
        user = User.objects.filter(email = input_value).first()
        return user

    else : # username is given check if student or staff or teacher or parent
        print(input_value)
        user = User.objects.filter(username = input_value).first()
        return user

# it requires email,otp sent and password to provide acesss token for the user
# create account and varify email and activate the user 
class RegisterVerifyView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self, request, format=None):
        try:
            # fields required 
            username_field = request.data.get('username_field',None)
            email_verification_code = request.data.get('otp',None)
            password = request.data.get('password',None)
            
            user = find_user_by_email_username(username_field) 
            if not user : # user not found by the given info 
                return Response({'error' : 'User not found!',},status=status.HTTP_200_OK)
            authenticated = user.verificationcode.checkCode(email_verification_code)
             # heck if otp is not expired in 10mints 
            if user.verificationcode.is_expired():
                    return Response({'error' : 'otp has expired! request another ',},status=status.HTTP_200_OK)
            
            if user and authenticated  : # verify the Email now 
                user.email_varified = True
                user.is_active = True 
                # change verification code (optional)
                user.verificationcode.setCode(generate_5_otp())
                user.save()
                
                # check if its valid password 
                if not user.check_password(password) :
                    return Response({"error":'wronge password!'},status=status.HTTP_200_OK)
                
                tokens = create_jwt_tokens_for_user(user)
                #we send email here for a user successful account creation
                #send email here 
                try:
                    html_content = generate_registration_email(user.username,'')
                    send_html_email.delay(
                        subject="🔐 Wellcome to the App",
                        to_email=user.email,
                        html_content=html_content
                    )
                except :
                    pass
                data = serialize_with_role(user,user.role)
                if not data :
                    return Response({'error' : "user role data not found!"},status=status.HTTP_200_OK)
                return Response({ # Email verified
                    'success' : " Email verified",
                    'data' : {"role":user.role,"tokens":tokens, "data":data}
                },status=status.HTTP_201_CREATED)
            else :
                # print('failed verification ')
                return Response({'error' : "authentication failed!"},status=status.HTTP_200_OK)
        except :
           return Response({"error":"server went wrong"},status=status.HTTP_200_OK)
       
# this view is used to create  retrive otp if not expired if expired generate new one
# if MODE field is specipied it will generate new nomatter how 
# for both authorised and non authorized users , 
# unauthorized request need with different credentials to verify the user before sending otp
class RetriveOrGenOTPView(APIView) :
    permission_classes=[permissions.AllowAny]
    def post(self, request, format=None):
        try:
            retrive_opt = False
            # check if user is logged in  
            user = request.user 
            user_found = request.user.is_authenticated
            retrive_opt = True if user_found else False 
            
            if not user_found : # user not logged in 
                username_field = request.data['username_field']
                operation_mode = request.data.get('operation_mode',None)
                
                user = find_user_by_email_username(username_field) 
                if not user : # user not found by the given info 
                # print('user: ', user)
                    return Response({
                        'error' : 'user not found!',
                    },status=status.HTTP_200_OK)
                retrive_opt = True
                    
            if  retrive_opt : 
                    # check if current otp is still valid not expired  if so generate new and send 
                    if operation_mode :
                        email_verification_code = generate_5_otp()
                        
                    elif not user.verificationcode.is_expired() :
                        email_verification_code = user.verificationcode.code
                        
                    else :
                        email_verification_code = generate_5_otp()
                        
                    user.verificationcode.setCode(email_verification_code) 
                    user.save() 
                    # we send email with email_verification_code
                    try:
                        html_content = generate_otp_email(user.username,email_verification_code)
                        send_html_email.delay(
                            subject="🔐 Your Fentech OTP Code",
                            to_email=user.email,
                            html_content=html_content
                        )
                    except :
                        pass
                        # return Response({"error":"OTP not Sent!"},status=status.HTTP_200_OK)
                    print(' retrived :  ',email_verification_code)
                    return Response({"success":"otp_sent",},status=status.HTTP_200_OK)
        except:
            return Response({"error":"server went wrong"},status=status.HTTP_200_OK)
        
# the view check if email or id for login matches the password 
# will send the otp if user enable otp upon login ,also   if otp is provided then will login the user (2 possible request with otp and without)
# also if no otp requred on login if credentials are verified it will provide access token as login details 
class LoginRequestView(APIView):
    permission_classes =[permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        # try :
            username_field = request.data.get('username_field',None)
            # username_field = username_field.lower() if username_field else None
            print('username_field: ', username_field)
            password = request.data.get('password',None)
            otp = request.data.get('otp',None)
            
            user = find_user_by_email_username(username_field) 
            if not user : # user not found by the given info 
                 return Response({'error' : 'User details not found!',},status=status.HTTP_200_OK)
           
            #---------------------user found ------------------------
            verified_password = user.check_password(password) 
            if not verified_password :
                    return Response ({'error':'wrong password!',} , status = status.HTTP_200_OK )
                    
            if not user.email_varified :
                # user exists but unverified email(incomplate registration )
                email_verification_code = generate_5_otp()
                verification_obj, created = VerificationCode.objects.get_or_create(user=user)
                verification_obj.setCode(email_verification_code)
                verification_obj.save()
                # we send email with email_verification_code
                try:
                    html_content = generate_otp_email(user.username,email_verification_code)
                    send_html_email.delay(
                        subject="🔐Verify  Your Fentech Email with  Code",
                        to_email=user.email,
                        html_content=html_content
                    )
                except :
                    pass
                    # return Response({'error':'Otp not sent '},status=status.HTTP_200_OK)
                        
                print(email_verification_code) 
                return Response({
                    "success":"incomplete_registration",
                    'email' :user.email,
                    "redirect_to": reverse("register-verify")
                    },status=status.HTTP_200_OK)
                    
            # password is correct and email is verified 
            # start logging in  #  check if its with otp 
            if user.otp_required and not otp : #we need otp  its otp request 
                generated_otp = generate_5_otp()
                verification_obj, created = VerificationCode.objects.get_or_create(user=user)
                verification_obj.setCode(generated_otp)
                verification_obj.save()
                print('generated_otp: ', generated_otp)
                # we will send otp to the user email
                # send otp here 
                try:
                    html_content = generate_otp_email(user.username,generated_otp)
                    send_html_email.delay(
                        subject="🔐 Your EDUPORTAL Login OTP Code",
                        to_email=user.email,
                        html_content=html_content
                    )
                except : 
                    pass
                
                return Response ({
                    'success':'otp_sent',
                    'user_email' : f'{user.email}',
                    "redirect_to" : reverse('login-requests') 
                },status= status.HTTP_200_OK)
                
            elif user.otp_required and otp : #otp is obtained 
                if user.verificationcode.checkCode(otp): # otp verified
                    # check if otp is not expired in 10mints 
                    if user.verificationcode.is_expired():
                         return Response({
                            'error' : 'otp has expired! request another ',
                        },status=status.HTTP_200_OK)
                    user.verificationcode.setCode(generate_5_otp())
                    user.save()
                    # send login message 
                    try:
                        html_content = generate_login_email(user.username,'')
                        send_html_email.delay(
                            subject="🔐 Account login",
                            to_email=user.email,
                            html_content=html_content
                        )
                    except :
                        pass
                    # check if user is active to login 
                    if user and not user.is_active : # account inactive
                        return Response({
                            'error' : 'user is inactive contact support!',
                        },status=status.HTTP_200_OK) 
                    # generate this user access tokens 
                    tokens = create_jwt_tokens_for_user(user)
                    data = serialize_with_role(user,user.role)        
                    if not data :
                        return Response({'error' : "user role data not found!"},status=status.HTTP_200_OK)
                    return Response({
                        'success' : 'Login Successfully ',
                        'data' : {"role":user.role,"tokens":tokens,"data":data},
                    },status=status.HTTP_200_OK)
                else :
                    return Response({"error":"invalid otp"},status=status.HTTP_200_OK)
            
            # we dont need otp to login 
            elif not user.otp_required :
                    tokens = create_jwt_tokens_for_user(user)
                    user = UserSerializer(user).data
                    # check user role to provide dta 
                    data = serialize_with_role(user,user.role)  
                    if not data :
                        return Response({'error' : "user role data not found!"},status=status.HTTP_200_OK)
                    return Response({
                        'success' : 'Login Successfully ',
                        'data' : {"role":user.role, "tokens":tokens,"data":data},
                    },status=status.HTTP_200_OK)
            else :
               return Response({'error':'login failed!'},status=status.HTTP_200_OK)
        # except :
            # return Response({"error":"server went wrong"})
class SearchUserView(APIView):
    def post(self, request):
        try:
            user = None
            search = request.data.get('search',None)
            user = find_user_by_email_username(search)
            if user is None : 
                print('user not found try his Account_id')
                user = User.objects.filter(account__account_id = search).first()
            if user :
                user = UserSerializer(user).data
                return Response(user,status=status.HTTP_200_OK)
            else :
                return Response({"error":"user not found "}, status=status.HTTP_200_OK)
        except :
           return Response({"error":"server failed "},status=status.HTTP_200_OK)
       
# it changes password for both authenticated and non authenticated users
# both have their specific requirements base on their authentication status
# if authenticated we need , current password , and otp
# if not authenticated we need username field to find the user and otp
# OTP will also be sent to their resfective email before changing the password
class PasswordChangeView(APIView):
    # permission_classes =[permissions.AllowAny]
    def post( self, request,format=None ):
        try:
            user = request.user
            authenticated_user = user.is_authenticated
            
            # fields required 
            username_field = request.data.get('username_field',None) # for reset
            current_password = request.data.get('currentCodes',None) # for change
            password1 = request.data.get('code1',None) # for Change and reset
            password2 = request.data.get('code2',None) # for Change and reset
            otp = request.data.get('verificationCode',None) #  for Change and reset is required at final step 
            operation_mode = request.data.get('operation_mode','reset') # reset or change
            
            if (len(password1) < 8) :
                return Response({"error":"new password must be > 8 "},status=status.HTTP_200_OK)
            if not (password1 == password2) :
                return Response({"error":"New Password Mismatched"},status=status.HTTP_200_OK)  
            
            # ------------------------  change operation    ----------------------
            if operation_mode == 'change' :
                if not authenticated_user :
                    return Response({"error":"user not authenticated"},status=status.HTTP_200_OK)
                else :
                    # verify and change password
                    if (not user.check_password(current_password)) :
                        return Response({"error":"Wronge Password!"},status=status.HTTP_200_OK)
                    # verify the otp 
                    if (not user.verificationcode.checkCode(otp) or user.verificationcode.is_expired()) :
                        return Response({"error":"invalid/expired otp"},status=status.HTTP_200_OK)
                    user.set_password(password1)
                    user.save()
            
            # -------------------- reset operation dont force authentication ----------------
            elif operation_mode == 'reset' :
                # find the user from field 
                user = find_user_by_email_username(username_field) 
                if not user : # user not found by the given info 
                    return Response({
                        'error' : 'user not found!',
                    },status=status.HTTP_200_OK)
                    
                if (not user.verificationcode.checkCode(otp) or user.verificationcode.is_expired()) :
                        return Response({"error":"invalid/expired otp"},status=status.HTTP_200_OK)
                user.set_password(password1)
                user.save()
            else :
                return Response({"error":"invalid operation mode"},status=status.HTTP_200_OK) 
            # send email here 
            try:
                html_content = generate_login_email(user.username,'')
                send_html_email.delay(
                    subject="🔐 Password Changed",
                    to_email=user.email,
                    html_content=html_content
                )
            except :
                pass
            return Response({"success":"Password Changed","mode":operation_mode},status=status.HTTP_200_OK)
        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)
class ProfileUpdateView(APIView):
        parser_classes =[MultiPartParser,FormParser]
        def put(self, request):
            try:
                user = request.user
                new_picture = request.data.get('file',None)
                first_name = request.data.get('first_name',None)
                last_name = request.data.get('last_name',None)
                if user :
                    if new_picture :
                        user.picture = new_picture
                    if first_name:
                        user.first_name = first_name
                    if last_name :
                        user.last_name = last_name 
                    user.save()
                    updated_user = UserSerializer(user).data
                    return Response({"success":"profile updated",'user':updated_user},status=status.HTTP_200_OK)
                else :
                    return Response({"error":"user not found!"},status=status.HTTP_200_OK)
            except :
                return Response({"error":"server failed"},status=status.HTTP_200_OK)

class CurrentUserView(APIView):
    def get(self, request,format=None):
        try:
            current_user = User.objects.get(id = request.user.id)
            user_serializer = UserSerializer(current_user).data
            return Response(user_serializer,status=status.HTTP_200_OK)
        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)


# class ManageUserLogin(APIView):
#     # permission_classes =[permissions.AllowAny]
#     def post(self, request,format=None):
#         try:
#             user = request.user
#             payment_pin = request.data.get('payment_pin')
#             otp_required = request.data.get('otp_required')
            
#             if (not user.userpins.checkPin(payment_pin)) :
#                 return Response({"error":"pin not correct! reset the pin if you forget "},status=status.HTTP_200_OK)
            
#             # update the user login setting 
#             user.otp_required = otp_required
#             user.save()
#             user_serializer = UserSerializer(user)
#             try:
#                 html_content = generate_login_email(user.username,'')
#                 send_html_email.delay(
#                     subject=f"🔐 Login Setting  Updated!",
#                     to_email=user.email,
#                     html_content=html_content
#                 )
#             except :
#                 pass
#             return Response({"success":f"success",'user':user_serializer.data},status=status.HTTP_200_OK)
#         except :
#            return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)


# class PinChangeView(APIView):
#     # permission_classes =[permissions.AllowAny]
#     def post(self, request,format=None):
#         try:
#             user = request.user
            
#             current_pin = request.data.get('currentCodes')
#             codes1 = request.data.get('codes1')
#             codes2 = request.data.get('codes2')
#             mode = request.data.get('mode')
#             otp = request.data.get('verificationCode')
            
#             if mode == 'reset' :
#                 if (not user.verificationcode.checkCode(otp)) :
#                     return Response({"error":"invalid otp"},status=status.HTTP_200_OK)
#                  # check if otp is not expired in 10mints          
                # if user.verificationcode.is_expired():
                #   return Response({'error' : 'otp has expired! request another ',},status=status.HTTP_200_OK)
            
#             else : #mode == change 
#                 if (codes1 ==  current_pin) :
#                     return Response({"error":"New Pin and Current Pin must be different"},status=status.HTTP_200_OK)
#                 if (not user.userpins.checkPin(current_pin)) :
#                     return Response({"error":"pin not correct! reset the pin if you forget "},status=status.HTTP_200_OK)
                
#             if (codes1 == codes2) :
#                     user.payment_pin_set =  True
#                     user.userpins.setPin(codes1)
#                     print(f"Pin {mode} successfully")
#                         # send Email here 
#                     try:
#                         html_content = generate_login_email(user.username,'')
#                         send_html_email.delay(
#                             subject=f"🔐 {mode} successfully ",
#                             to_email=user.email,
#                             html_content=html_content
#                         )
#                     except :
#                         pass
                    
#                     return Response({"success":f"Pin {mode} successfully"},status=status.HTTP_200_OK)
#             else :
#                 return Response({"error":"pins mismatched"},status=status.HTTP_200_OK)

#         except :
#            return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)



