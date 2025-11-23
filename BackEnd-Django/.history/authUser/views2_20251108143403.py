from functools import partial
# from logging import raiseExceptions
import os ,random,re
from datetime import timedelta

from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken  # or your preferred JWT lib

# core app
# views.py or any view file

from core.emails.email_templates.emails import generate_otp_email,generate_login_email,generate_registration_email
from core.emails.utils.email_service import send_html_email


from .serializers import UserSerializer, MiniUserSerializer
# from notifications.serializers import NotificationSerializer
# from notifications.models import Notification
# from account.websocketandmail import signal_sender
# from account.models import MoneyTransaction
# from account.serializers import MoneyTransactionSerializer
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from .models import User

# Create your views here.

def create_jwt_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
def generate_verification_code() :
    code = random.randint(12345,98769)
    return  code 

def identify_field_type(input_value):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'  # Basic email pattern
    phone_regex = r'^\+?\d{10,15}$'  # Matches 10-15 digits, optional '+'
    username_regex = r'^[a-zA-Z0-9_]{3,30}$'  # Alphanumeric and underscores, 3-30 chars

    if re.match(email_regex, input_value):
        user = User.objects.filter(email = input_value).first()
        return user if user else None

    elif re.match(phone_regex, input_value):
        user = User.objects.filter(phone_number = input_value).first()
        return user if user else None

    elif re.match(username_regex, input_value):
        user = User.objects.filter(username = input_value).first()
        return user if user else None
    else:
        return None

class VerifyWithEmailOtp(APIView):
    def post(self, request):
        # try:
            user = request.user
            redirect_link_name = request.data.get('redirect_to')
            email = request.data.get('email')
            if not user : # user is not logged in try finding him by email
                try:
                    user = User.objects.get(email = email)
                except User.DoesNotExist:
                    return Response({"error":"user not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if user.email ==  email :
                    email_verification_code = generate_verification_code() 
                    user. email_verification_code =  email_verification_code 
                    user.save()
                    # we send email with email_verification_code
                    # send email here 
                    try:
                        html_content = generate_otp_email(user.username,email_verification_code)
                        send_html_email.delay(
                            subject="🔐 Your Fentech OTP Code",
                            to_email=user.email,
                            html_content=html_content
                        )
                    except :
                        pass
                    
                    print(user.email_verification_code)
                    link= ''
                    try :
                        link = reverse(f"{redirect_link_name}")
                    except :
                        pass
                    return Response({
                    "success":"otp_sent",
                        "redirect_to":  link if link else 'not set '
                        },status=status.HTTP_200_OK)
            else :
                return Response({"error":"use your verified email "},status=status.HTTP_200_OK)
        # except :
        #    return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)

class RegisterView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self, request, format=None):
        try:
            email = request.data['email'].lower()
            phone_number = request.data['phone_number']
            username = request.data['username'].lower()
            first_name = request.data['firstName'].lower()
            last_name = request.data['lastName'].lower()
            password = request.data['password']
            password2 = request.data['password2']
            refarrel_code = request.data['refarrel_code']
            
            try :
                emailfound = User.objects.filter(email = email).exists()
                phone_number_found = User.objects.filter(phone_number = phone_number).exists()
                usernamefound = User.objects.filter(username = username).exists() 
                
                user = User.objects.get(email = email)
                email_varified =user.email_varified  == True
            except :
                user = None
                
            # user exist with not verified email
            if user and not email_varified :
                email_verification_code = generate_verification_code()
                user.email_verification_code =  email_verification_code 
                user.save()
                # we send email with email_verification_code
                # send email here 
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
                        
                print(user.email_verification_code)
                return Response({
                    "success":"incomplete_registration",
                    'email' :user.email,
                    "redirect_to": reverse("register-verify")
                    },status=status.HTTP_200_OK)
            
            if not usernamefound : #username not selected
                if not emailfound  and not phone_number_found:# username not selected
                    if len(password) >= 8 and (password == password2):
                            email_verification_code = generate_verification_code()
                            newuser = User.objects.create_user(
                                first_name=first_name,
                                last_name=last_name,    
                                email=email,
                                phone_number = phone_number,
                                username=username,
                                password=password,
                                email_verification_code = email_verification_code
                            )
                            # handle refarrel program now 
                            inviter = User.objects.filter(refarrel_code = refarrel_code).exists()
                            if refarrel_code  and inviter :
                                User.objects.get(refarrel_code =refarrel_code).refarrels.add(newuser.id)
                                
                            # we send email with email_verification_code
                            # send email here 
                            try:
                                html_content = generate_otp_email(user.username,email_verification_code)
                                send_html_email.delay(
                                    subject="🔐 Verify Your Fentech Email With  OTP Code",
                                    to_email=user.email,
                                    html_content=html_content
                                )
                            except :
                                pass
                            print(email_verification_code)
                            
                            return Response({
                                "success":"otp_sent",
                                "redirect_to": reverse('register-verify')
                                },status=status.HTTP_200_OK)
                    else :
                        return Response({'error' : "passwords short or mis matched!"},status=status.HTTP_200_OK)
                else:
                    return Response({'error' : "Email or Phone number already exists"},status=status.HTTP_200_OK)

            else:
                return Response({'error' : "username already exists"},status=status.HTTP_200_OK)
        except:
            return Response({"error":"server went wrong"},status=status.HTTP_200_OK)
        
class VerifyWithEmailOtp(APIView):
    def post(self, request):
        # try:
            user = request.user
            redirect_link_name = request.data.get('redirect_to')
            email = request.data.get('email')
            if not user : # user is not logged in try finding him by email
                try:
                    user = User.objects.get(email = email)
                except User.DoesNotExist:
                    return Response({"error":"user not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if user.email ==  email :
                    email_verification_code = generate_verification_code() 
                    user. email_verification_code =  email_verification_code 
                    user.save()
                    # we send email with email_verification_code
                    # send email here 
                    try:
                        html_content = generate_otp_email(user.username,email_verification_code)
                        send_html_email.delay(
                            subject="🔐 Your Fentech OTP Code",
                            to_email=user.email,
                            html_content=html_content
                        )
                    except :
                        pass
                    
                    print(user.email_verification_code)
                    link= ''
                    try :
                        link = reverse(f"{redirect_link_name}")
                    except :
                        pass
                    return Response({
                    "success":"otp_sent",
                        "redirect_to":  link if link else 'not set '
                        },status=status.HTTP_200_OK)
            else :
                return Response({"error":"use your verified email "},status=status.HTTP_200_OK)
        # except :
        #    return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)

class RetriveOtpView(APIView) :
    permission_classes=[permissions.AllowAny]
    def post(self, request, format=None):
        try:
            retrive_opt = False
            # check if user is logged in  
            user=request.user 
            user_found = request.user.is_authenticated
            retrive_opt = True if user_found else False 
            
            if not user_found : #usernot logged in 
                username_field = request.data['username_field'].lower()
                password = request.data.get('password')
                
                found = True if User.objects.filter(
                    email = username_field
                ).exists() else True if  User.objects.filter(
                    username = username_field
                ).exists() else True if  User.objects.filter(
                    phone_number = username_field
                ).exists() else False 
                
                user = identify_field_type(username_field)  if found else None
                verified_password = user.check_password(password) if found else None
                if not user : # user not found by the goven info 
                    return Response({
                        'error' : 'user not  Found',
                    },status=status.HTTP_200_OK)
            
                if not verified_password :
                        return Response ({'error':'wrong password',} 
                    , status = status.HTTP_200_OK )
                
                retrive_opt = True
                    
            if  retrive_opt :
                    email_verification_code = user.email_verification_code  
                    # we send email with email_verification_code
                    try:
                        html_content = generate_otp_email(user.username,email_verification_code)
                        send_html_email.delay(
                            subject="🔐 Your Fentech OTP Code",
                            to_email=user.email,
                            html_content=html_content
                        )
                    except :
                        return Response({"error":"OTP not Sent!"},status=status.HTTP_200_OK)
                    print(user. email_verification_code)
                    return Response({"success":"otp_sent",},status=status.HTTP_200_OK)
        except:
            return Response({"error":"server went wrong"},status=status.HTTP_200_OK)
    
class RegisterVerifyView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self, request, format=None):
        # try:
            email = request.data['email'].lower()
            print('email: ', email)
            email_verification_code = request.data['otp']
            password = request.data.get('password',None)
            try :
                user = User.objects.get(email = email)
                authenticated = str(user.email_verification_code) == str(email_verification_code)
            except :
                user = None
            
            if user and authenticated and not user.email_varified :
                user.email_varified = True
                user.is_active = True
                # change verification code 
                user.email_verification_code = generate_verification_code()
                user.save()
                print("account successfully created")
                
                # check if its valid password 
                if not  user.check_password(password) :
                    return Response({"error":'wronge password'},status=status.HTTP_200_OK)
                
                tokens = create_jwt_tokens_for_user(user)
                user_data = UserSerializer(user).data
                #we send email here for a user successful account creation
                #send email here 
                try:
                    html_content = generate_registration_email(user.username,'')
                    send_html_email.delay(
                        subject="🔐 Wellcome to Fintech app",
                        to_email=user.email,
                        html_content=html_content
                    )
                except :
                    pass
                return Response({
                    'success' : "accountCreated",
                    'data' : {"tokens":tokens, "user":user_data}
                },status=status.HTTP_201_CREATED)
            else :
                 return Response({'error' : "email verification failed check again"},status=status.HTTP_200_OK)
        # except :
        #    return Response({"error":"server went wrong"},status=status.HTTP_200_OK)
 
class LoginRequestView(APIView):
    permission_classes =[permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        # try :
            username_field = request.data['username_field'].lower()
            password = request.data.get('password')
            otp = request.data.get('otp')
            
            found = True if User.objects.filter(
                email = username_field
            ).exists() else True if  User.objects.filter(
                username = username_field
            ).exists() else True if  User.objects.filter(
                phone_number = username_field
            ).exists() else False 
            
            user = identify_field_type(username_field)  if found else None
            verified_password = user.check_password(password) if user else None
            if not user : # user not found by the given info 
                 return Response({
                    'error' : 'user not  Found',
                },status=status.HTTP_200_OK)
            
            if not verified_password :
                    return Response ({'error':'wrong password',} 
                , status = status.HTTP_200_OK )
                    
            if not user.email_varified :
                # user exists but unverified email(incomplate registration )
                email_verification_code = generate_verification_code()
                user.email_verification_code = email_verification_code 
                user.save()
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
                        
                print(user.email_verification_code)
                return Response({
                    "success":"incomplete_registration",
                    'email' :user.email,
                    "redirect_to": reverse("register-verify")
                    },status=status.HTTP_200_OK)
                    
            # password is correct and email is verified 
            # start logging in  
            
            #  check if its with otp 
            if user.log_with_otp and not otp : #we need otp  its otp request 
                generated_otp = generate_verification_code()
                user.email_verification_code = generated_otp
                user.save()
                print('generated_otp: ', generated_otp)
                # we will send otp to the user email
                # send otp here 
                try:
                    html_content = generate_otp_email(user.username,generated_otp)
                    send_html_email.delay(
                        subject="🔐 Your Fentech  Login OTP Code",
                        to_email=user.email,
                        html_content=html_content
                    )
                except :
                    pass
                return Response ({
                    'success':'otp_sent',
                    'user_email' : f'{user.email}',
                    "redirect_to" : reverse('login') 
                },status= status.HTTP_200_OK)
            elif user.log_with_otp and otp : #otp is obtained 
                if user.email_verification_code == otp : # otp verified
                    user.email_verification_code = generate_verification_code()
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
                    tokens = create_jwt_tokens_for_user(user)
                    # check if user is active to login 
                    if user and not user.is_active : # account inactive
                        return Response({
                            'error' : 'user is in active contact support!',
                        },status=status.HTTP_200_OK)
                        
                    user = UserSerializer(user).data
                    return Response({
                        'success' : 'Login Successfully ',
                        'data' : {"tokens":tokens,"user":user},
                    },status=status.HTTP_200_OK)
                else :
                    return Response({"error":"invalid otp"},status=status.HTTP_200_OK)
            
            elif not user.log_with_otp :# we dont need otp to login 
                tokens = create_jwt_tokens_for_user(user)
                user = UserSerializer(user).data
                return Response({
                    'success' : 'Login Successfully',
                    'data' : {"tokens":tokens,"user":user},
                },status=status.HTTP_200_OK)
            else :
               pass
        # except :
            # return Response({"error":"server went wrong"})
   
class PasswordChangeView(APIView):
    # permission_classes =[permissions.AllowAny]
    def post(self, request,format=None):
        try:
            user = request.user
            current_password = request.data.get('currentCodes')
            password1 = request.data.get('codes1')
            password2 = request.data.get('codes2')
            mode = request.data.get('mode')
            otp = request.data.get('verificationCode')
            pin = request.data.get('payment_pin')
            
            if mode == 'reset' :
                if (not user.email_verification_code == otp) :
                    return Response({"error":"invalid otp"},status=status.HTTP_200_OK)
            else : #mode == change 
                if (not user.check_password(current_password)) :
                    return Response({"error":"Wronge Password!"},status=status.HTTP_200_OK)
                if (not user.checkPaymentPin(pin)) :
                    return Response({"error":"invalid pin"},status=status.HTTP_200_OK)
                if (password1 ==  current_password) :
                    return Response({"error":"New Password  and Current Password must be different"},status=status.HTTP_200_OK)
            if (len(password1) < 8) :
                return Response({"error":"New Password must be > 8 "},status=status.HTTP_200_OK)
            
            # now we can set the new Password 
            if (password1 == password2) :
                user.set_password(password1)
                user.save()
                # send Email here 
                try:
                    html_content = generate_login_email(user.username,'')
                    send_html_email.delay(
                        subject="🔐 Password Changed",
                        to_email=user.email,
                        html_content=html_content
                    )
                except :
                    pass
                        
                return Response({"success": f"Password {mode} successfully "},status=status.HTTP_200_OK)
            else :
                return Response({"error":"password mismatched"},status=status.HTTP_200_OK)
        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)


class SearchUserView(APIView):
    def post(self, request):
        try:
            user = None
            search = request.data.get('search')
            user = identify_field_type(search)
            if user is None : 
                print('user not found try his Account_id')
                user = User.objects.filter(account__account_id = search).first()
            if user :
                user = UserSerializer(user).data
                return Response(user,status=status.HTTP_200_OK)
            else :
                return Response({"error":"user not found"}, status=status.HTTP_200_OK)
        except :
           return Response({"error":"server failed"},status=status.HTTP_200_OK)
       

class PasswordResetView(APIView):
    # permission_classes =[permissions.AllowAny]
    def post(self, request,format=None):
        try:
            user = request.user
            password1 = request.data.get('password1')
            password2 = request.data.get('password2')
            email_otp = request.data.get('otp')
            user_pin = request.data.get('pin')
            
            if (user.email_verification_code == email_otp) :
                if user.che(user_pin) :
                    if (password1 == password2) :
                        user.set_password(password1)
                        user.email_verification_code = generate_verification_code() 
                        user.save()
                        # send Email here  of password reset success
                        try:
                            html_content = generate_login_email(user.username,'')
                            send_html_email.delay(
                                subject="🔐 Password Reset",
                                to_email=user.email,
                                html_content=html_content
                            )
                        except :
                            pass 
                        
                        return Response({"success":"Password Reset!"},status=status.HTTP_200_OK)
                    else :
                        return Response({"error":"New Password Mismatched"},status=status.HTTP_200_OK)
                else :
                    return Response({"error":"Incorrect Pins "},status=status.HTTP_200_OK)
            
            else :
                return Response({"error":"wronge otp"},status=status.HTTP_200_OK)
        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)

# here 
class PasswordForgetView(APIView):
    permission_classes =[permissions.AllowAny]
    def post(self, request,format=None):
        try:
            email = request.data.get('email')
            password1 = request.data.get('password1')
            password2 = request.data.get('password2')
            otp = request.data.get('otp')
            try :
                # check if user exists with the given email
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)
            
            if (user.email_verification_code == otp) :
                    if (password1 == password2) :
                        user.set_password(password1)
                        user.email_verification_code = generate_verification_code() 
                        user.save()
                        # send Email here  of password reset success 
                        try:
                            html_content = generate_login_email(user.username,'')
                            send_html_email.delay(
                                subject="🔐 Password Changed",
                                to_email=user.email,
                                html_content=html_content
                            )
                        except :
                            pass
                        
                        return Response({"success":"Password Reset!"},status=status.HTTP_200_OK)
                    else :
                        return Response({"error":"New Password Mismatched"},status=status.HTTP_200_OK)
            else :
                return Response({"error":"wronge pin"},status=status.HTTP_200_OK)

        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)

class PinChangeView(APIView):
    # permission_classes =[permissions.AllowAny]
    def post(self, request,format=None):
        try:
            user = request.user
            
            current_pin = request.data.get('currentCodes')
            codes1 = request.data.get('codes1')
            codes2 = request.data.get('codes2')
            mode = request.data.get('mode')
            otp = request.data.get('verificationCode')
            
            if mode == 'reset' :
                if (not user.email_verification_code == otp) :
                    return Response({"error":"invalid otp"},status=status.HTTP_200_OK)
            else : #mode == change 
                if (codes1 ==  current_pin) :
                    return Response({"error":"New Pin and Current Pin must be different"},status=status.HTTP_200_OK)
                if (not user.payment_pin ==  current_pin) :
                    return Response({"error":"pin not correct! reset the pin if you forget "},status=status.HTTP_200_OK)
                
            if (codes1 == codes2) :
                    user.payment_pin_set =  True
                    user.payment_pin =  codes1
                    user.save()
                    print(f"Pin {mode} successfully")
                        # send Email here 
                    try:
                        html_content = generate_login_email(user.username,'')
                        send_html_email.delay(
                            subject=f"🔐 {mode} successfully ",
                            to_email=user.email,
                            html_content=html_content
                        )
                    except :
                        pass
                    
                    return Response({"success":f"Pin {mode} successfully"},status=status.HTTP_200_OK)
            else :
                return Response({"error":"pins mismatched"},status=status.HTTP_200_OK)

        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)



class ProfileUpdateView(APIView):
        parser_classes =[MultiPartParser,FormParser]
        def put(self, request):
            try:
                user = request.user
                new_picture = request.data.get('file')
                first_name = request.data.get('first_name')
                last_name = request.data.get('last_name')
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
            return Response( user_serializer,status=status.HTTP_200_OK)
        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)


class ManageUserLogin(APIView):
    # permission_classes =[permissions.AllowAny]
    def post(self, request,format=None):
        try:
            user = request.user
            payment_pin = request.data.get('payment_pin')
            log_with_otp = request.data.get('log_with_otp')
            
            if (not user.payment_pin ==  payment_pin) :
                return Response({"error":"pin not correct! reset the pin if you forget "},status=status.HTTP_200_OK)
            
            # update the user login setting 
            user.log_with_otp = log_with_otp
            user.save()
            user_serializer = UserSerializer(user)
            try:
                html_content = generate_login_email(user.username,'')
                send_html_email.delay(
                    subject=f"🔐 Login Setting  Updated!",
                    to_email=user.email,
                    html_content=html_content
                )
            except :
                pass
            return Response({"success":f"success",'user':user_serializer.data},status=status.HTTP_200_OK)
        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)

