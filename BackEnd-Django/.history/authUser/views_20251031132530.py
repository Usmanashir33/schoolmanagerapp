from functools import partial
from logging import raiseExceptions
import os ,random,re
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import get_object_or_404 
from . import serializers

from .serializers import UserSerializer
from notifications.serializers import NotificationSerializer
from notifications.models import Notification
from account.websocketandmail import signal_sender
from account.models import MoneyTransaction
from account.serializers import MoneyTransactionSerializer
from rest_framework.views import APIView  
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from .models import User , KYC
from .serializers import MiniUserSerializer

# Create your views here.

def generate_verifed_email_otp() :
    code = random.randint(12345,98769)
    # code_exit = User.objects.get(email_verification_code = code).exists()
    return  code 
    # return  code if not code_exit else  generate_verifed_email_otp()

def identify_field_type(input_value):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'  # Basic email pattern
    phone_regex = r'^\+?\d{10,15}$'  # Matches 10-15 digits, optional '+'
    username_regex = r'^[a-zA-Z0-9_]{3,30}$'  # Alphanumeric and underscores, 3-30 chars

    if re.match(email_regex, input_value):
        user = User.objects.get(email = input_value)
        return user

    elif re.match(phone_regex, input_value):
        user = User.objects.get(phone_number = input_value)
        return user

    elif re.match(username_regex, input_value):
        user = User.objects.get(username = input_value)
        return user
    else:
        return None

def createInternalTrx (request,recipient):
    # send notification and update the user  via websocket
    user = request.user
    amount = request.data.get('amount')
    user_room = f"room{user.id}"
    recipient_room = f"room{recipient.id}"
    
    user_data = UserSerializer(user).data
    recipient_data = UserSerializer(recipient).data
    # create trx 
    user_trx = MoneyTransaction.objects.create(
        user = user,
        amount = f"{amount}",
        net_charges = 0.00,
        status = 'success',
        transaction_type = 'Transfer-Out',
        notes = request.data.get('note'),
        receiver = recipient
    )
    user_trx.save()
    recipient_trx = MoneyTransaction.objects.create(
        user = recipient,
        amount = f"{amount}",
        net_charges = 0.00,
        status = 'success',
        transaction_type = 'Transfer-In',
        notes = request.data.get('note')
    )
    recipient_trx.save()
    
    trx = MoneyTransactionSerializer(user_trx).data
    user_resp = {
        "trx":trx,
        "user":user_data
    }
    # for recipient responses 
    trx = MoneyTransactionSerializer(recipient_trx).data
    recipient_resp = {
        "type":"send_response",
        "signal_name" : 'money_trx',
        "trx":trx,
        "user":recipient_data
    }
    
    recipient_notif = Notification.objects.create(
        user = recipient,
        title = 'Internal Transfer Comfirmed',
        body =f'{user.username} has sent you {amount}',
        type = 'success'
    )
    recipient_notif.save()
    recipient_notif = NotificationSerializer(recipient_notif).data
    
    data2 = {
        "type":"send_response",
        "signal_name" : 'money_notif',
        "notif":recipient_notif,
        "user":user_data
    }
    signal_sender(recipient_room,data2) # send totic=fication to recipient
    signal_sender(recipient_room,recipient_resp) # send trx to reciepient
    return user_resp
 
class RegisterView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self, request, format=None):
        # print('request: ', request.data)
        # try:
            email = request.data['email'].lower()
            phone_number = request.data['phone_number']
            username = request.data['username'].lower()
            password = request.data['password']
            password2 = request.data['password2']
            refarrel_code = request.data['refarrel_code']
            try :
                emailfound = User.objects.filter(email = email).exists()
                phone_number_found = User.objects.filter(phone_number = phone_number).exists()
                usernamefound = User.objects.filter(username = username).exists() 
                user = User.objects.get(email = email)
                verified_email =user.email_varified  == True
            except :
                user = None
            if not usernamefound : #username not selected
                if not emailfound  and not phone_number_found:# username not selected
                    if len(password) >= 6 and (password == password2):
                            email_verification_code = generate_verifed_email_otp()
                            newuser = User.objects.create_user(
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
                            print(email_verification_code)
                            
                            return Response({
                                "success":"confirm_email",
                                "redirect_to": reverse('register-verify')
                                },status=status.HTTP_200_OK)
                    else :
                        return Response({'error' : "passwords short or mismatched!"},status=status.HTTP_200_OK)
                else:
                    if user and not verified_email : # user with not verified email
                        email_verification_code = generate_verifed_email_otp()
                        user. email_verification_code =  email_verification_code 
                        user.save()
                        # we send email with email_verification_code
                        # send email here 
                        
                        print(user.email_verification_code)
                        return Response({
                        "success":"confirm_email",
                            "redirect_to": reverse("register-verify")
                            },status=status.HTTP_200_OK)
                    return Response({'error' : "email or phone_number already exists"},status=status.HTTP_200_OK)
            else:
                if user and not verified_email : # user with not verified email
                    email_verification_code = generate_verifed_email_otp()
                    user. email_verification_code =  email_verification_code 
                    user.save()
                    # we send email with email_verification_code
                    # send email here 
                    
                    print(user.email_verification_code)
                    return Response({
                    "success":"confirm_email",
                        "redirect_to": reverse("register-verify")
                        },status=status.HTTP_200_OK)
                return Response({'error' : "username already exists"},status=status.HTTP_200_OK)
        # except:
            # return Response({"error":"server went wrong"},status=status.HTTP_200_OK)
    
class RegisterVerifyView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        try:
            email = request.data['email'].lower()
            email_verification_code = request.data['otp']
            try :
                user = User.objects.get(email = email)
                authenticated = str(user.email_verification_code) == str( email_verification_code)
            except :
                user = None
            
            if user and authenticated and not user.email_varified :
                user.email_varified = True
                user.is_active = True
                user.email_verification_code = generate_verifed_email_otp()
                user.save()
                #we send email here for a user successful account creation
                #send email here 
                print("account successfully created")
                print(user.email_verification_code)
                
                return Response({
                    'success' : "accountCreated",
                    'user_email' : user.email,
                    'login_otp' : f"{user.email_verification_code}",
                    "redirect_to": reverse('login')
                },status=status.HTTP_201_CREATED)
            else :
                 return Response({'error' : "email verification failed check again"},status=status.HTTP_400_BAD_REQUEST)
        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)
 
class LoginRequestView(APIView):
    permission_classes =[permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        try :
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
            
            if user and user.log_with_otp :
                if user and not verified_password :
                    return Response (
                {'success':'only_email_verified',} 
                , status = status.HTTP_200_OK )
                    
                if user and not user.email_varified :
                    email_verification_code = generate_verifed_email_otp() 
                    user. email_verification_code =  email_verification_code 
                    user.save()
                    # we send email with email_verification_code
                    # send email here 
                    
                    print(user.email_verification_code)
                    return Response({
                    "success":"confirm_email",
                        "redirect_to": reverse("register-verify")
                        },status=status.HTTP_200_OK)
                     
                generated_otp = generate_verifed_email_otp()
                print('generated_otp: ', generated_otp)
                # we will send otp to the user email
                # send otp here 
                user.email_verification_code = generated_otp
                user.save()
                
                return Response ({
                    'success':'email_sent',
                    'user_email' : f'{user.email}',
                    "redirect_to" : reverse('login') 
                },status= status.HTTP_200_OK)
            
            elif user and not user.log_with_otp :
                if user and not user.email_varified :
                    email_verification_code = generate_verifed_email_otp()
                    user. email_verification_code =  email_verification_code 
                    user.save()
                    # we send email with email_verification_code
                    # send email here 
                    
                    print(user.email_verification_code)
                    return Response({
                    "success":"confirm_email",
                        "redirect_to": reverse("register-verify")
                        },status=status.HTTP_200_OK)
                    
                if user and not verified_password :
                     return Response ({
                    'success':'only_email_verified',
                    },status= status.HTTP_200_OK)
                else:
                    return Response({
                        'success' : 'login',
                        'user_email' : f'{user.email}',
                        "redirect_to" : reverse('login') 
                    },status=status.HTTP_200_OK)
            else :
                return Response({
                    'error' : 'user not  Found',
                },status=status.HTTP_200_OK)
        except :
            return Response({"error":"server went wrong"})
   
class CurrentUserView(APIView):
    permission_classes =[permissions.AllowAny]
    def get(self, request,format=None):
        try:
            current_user = User.objects.get(id = request.user.id)
            user_serializer = serializers.UserSerializer(current_user).data
            return Response( user_serializer,status=status.HTTP_200_OK)
        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)


class PasswordChangeView(APIView):
    # permission_classes =[permissions.AllowAny]
    def post(self, request,format=None):
        try:
            # user = User.objects.get(id = request.user.id)
            user = request.user
            # user = User.objects.get(id = user.idsetConfirmPassword)
            
            curent_password = request.data.get('currentPassword')
            password1 = request.data.get('password1')
            password2 = request.data.get('password2')
            pin = request.data.get('pin')
            
            if (user.check_password(curent_password)) :
                if (user.payment_pin == pin) :
                    if (password1 == password2) :
                        user.set_password(password1)
                        user.save()
                        # send Email here 
                        
                        
                        return Response({"success":"Password Updated!"},status=status.HTTP_200_OK)
                    else :
                        return Response({"error":"password mismatched"},status=status.HTTP_200_OK)
                else :
                    return Response({"error":"wronge pin"},status=status.HTTP_200_OK)
            else :
                return Response({"error":"wronge password"},status=status.HTTP_200_OK)
        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)

class PasswordResetRequestView(APIView):
    # permission_classes =[permissions.AllowAny]
    def post(self, request,format=None):
        try:
            user = request.user
            email = request.data.get('email')
            
            if user.email ==  email :
                    email_verification_code = generate_verifed_email_otp() 
                    user. email_verification_code =  email_verification_code 
                    user.save()
                    # we send email with email_verification_code
                    # send email here 
                    
                    print( user.email_verification_code )
                    return Response({
                    "success":"confirm_email",
                        "redirect_to": reverse("password-reset")
                        },status=status.HTTP_200_OK)
            else :
                return Response({"error":"use your verified email "},status=status.HTTP_200_OK)

        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)

class PasswordResetView(APIView):
    # permission_classes =[permissions.AllowAny]
    def post(self, request,format=None):
        try:
            user = request.user
            
            password1 = request.data.get('password1')
            password2 = request.data.get('password2')
            pin = request.data.get('pin')
            
            if (user.email_verification_code == pin) :
                    if (password1 == password2) :
                        user.set_password(password1)
                        user.email_verification_code = generate_verifed_email_otp() 
                        user.save()
                        # send Email here  of password reset success 
                        
                        
                        return Response({"success":"Password Reset!"},status=status.HTTP_200_OK)
                    else :
                        return Response({"error":"New Password Mismatched"},status=status.HTTP_200_OK)
            else :
                return Response({"error":"wronge pin"},status=status.HTTP_200_OK)

        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)

class PasswordForgetRequestView(APIView):
    permission_classes =[permissions.AllowAny]
    def post(self, request,format=None):
        try:
            email = request.data.get('email')
            try :
                user = User.objects.get(email = email)
            except  Exception:
                return Response({"error":"email not found "},status=status.HTTP_200_OK)
                
            if user :
                    email_verification_code = generate_verifed_email_otp() 
                    user. email_verification_code =  email_verification_code 
                    user.save()
                    # we send email with email_verification_code
                    # send email here 
                    
                    print( user.email_verification_code )
                    return Response({
                    "success":"confirm_email",
                        "redirect_to": reverse("password-forget")
                        },status=status.HTTP_200_OK)
            else :
                return Response({"error":"email not found "},status=status.HTTP_200_OK)

        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)

class PasswordForgetView(APIView):
    permission_classes =[permissions.AllowAny]
    def post(self, request,format=None):
        try:
            email = request.data.get('email')
            password1 = request.data.get('password1')
            password2 = request.data.get('password2')
            pin = request.data.get('pin')
            user = User.objects.get(email = email)
            
            if (user.email_verification_code == pin) :
                    if (password1 == password2) :
                        user.set_password(password1)
                        user.email_verification_code = generate_verifed_email_otp() 
                        user.save()
                        # send Email here  of password reset success 
                        
                        
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
            
            curent_password = request.data.get('currentPassword')
            password1 = request.data.get('password1')
            password2 = request.data.get('password2')
            pin = request.data.get('pin')
            
            if (user.payment_pin ==  curent_password) :
                if (user.payment_pin == pin) :
                    if (password1 == password2) :
                        user.payment_pin =  password1
                        user.save()
                        # send Email here 
                        
                        
                        return Response({"success":"Pin Updated!"},status=status.HTTP_200_OK)
                    else :
                        return Response({"error":"pin mismatched"},status=status.HTTP_200_OK)
                else :
                    return Response({"error":"wronge pin"},status=status.HTTP_200_OK)
            else :
                return Response({"error":"wronge pin"},status=status.HTTP_200_OK)
        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)

class PinResetRequestView(APIView):
    # permission_classes =[permissions.AllowAny]
    def post(self, request,format=None):
        try:
            user = request.user
            email = request.data.get('email')
            
            if user.email ==  email :
                    email_verification_code = generate_verifed_email_otp() 
                    user. email_verification_code =  email_verification_code 
                    user.save()
                    # we send email with email_verification_code
                    # send email here 
                    
                    print( user.email_verification_code )
                    return Response({
                    "success":"confirm_email",
                        "redirect_to": reverse("pin-reset")
                        },status=status.HTTP_200_OK)
            else :
                return Response({"error":"use your verified email "},status=status.HTTP_200_OK)

        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)

class PinResetView(APIView):
    # permission_classes =[permissions.AllowAny]
    def post(self, request,format=None):
        try:
            user = request.user
            
            password1 = request.data.get('password1')
            password2 = request.data.get('password2')
            pin = request.data.get('pin')
            
            if (user.email_verification_code == pin) :
                    if (password1 == password2) :
                        user.payment_pin = password1
                        user.email_verification_code = generate_verifed_email_otp() 
                        user.save()
                        # send Email here  of password reset success 
                        
                        
                        return Response({"success":"Pn Reset!"},status=status.HTTP_200_OK)
                    else :
                        return Response({"error":"New Pin Mismatched"},status=status.HTTP_200_OK)
            else :
                return Response({"error":"wronge pin"},status=status.HTTP_200_OK)

        except :
           return Response({"error":"server went wrong"},status=status.HTTP_408_REQUEST_TIMEOUT)

class SearchUserView(APIView):
    def post(self, request):
        try:
            search = request.data.get('search')
            try:
                user = identify_field_type(search)
            except:
                user = None
            if not user : 
                user = User.objects.filter(account__account_id = search).first()
            if user :
                user = MiniUserSerializer(user).data
                return Response(user,status=status.HTTP_200_OK)
            else :
                return Response({"error":"user not found"}, status=status.HTTP_200_OK)
        except :
           return Response({"error":"user not found"},status=status.HTTP_200_OK)
class ProfilePictureView(APIView):
        parser_classes =[MultiPartParser,FormParser]
        def put(self, request):
            try:
                user = request.user
                new_picture = request.data.get('new_profile_pic')
                if new_picture :
                    user.picture = new_picture
                    user.save()
                    updated_user = MiniUserSerializer(user).data
                    return Response({"success":"profile picture updated",'user':updated_user},status=status.HTTP_200_OK)
                else :
                    return Response({"error":"user not found"}, status=status.HTTP_200_OK)
            except :
                return Response({"error":"user not found"},status=status.HTTP_200_OK)
           
 