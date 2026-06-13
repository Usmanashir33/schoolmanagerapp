# from logging import raiseExceptions
from django.utils import timezone

from django.db.models import Q

# core app
# views.py or any view file
from core.emails.email_templates.emails import generate_otp_email
from core.emails.email_templates.emails import generate_school_update_email
from core.tasks import send_html_email,send_ordinary_sms
from core.formatters import format_serializer_errors
from core.permissions import DirectorUserPermission
from core.serializers import DirectorSerializer
from core.utils.otp_generators import generate_5_otp

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from school.models import School 
from authUser.models import User

from school.models import School
from .serializers import DirectorDetailSerializer
#==================================================================================================            
#                                       DIRECTOR  SECTION                           
#==================================================================================================

class DirectorDetailView(APIView) :
    parser_classes =[MultiPartParser,FormParser]
    permission_classes=[
        permissions.IsAuthenticated,
        DirectorUserPermission,
    ]
    # ---------------- DIRECTOR SECTION -----------------
    def put(self, request):
        # if otp is provided we proceed ,if not we send otp 
        try : 
            director = request.user.director
            user = request.user
            # data = request.data.copy()
            pin = request.data.get("pin")
            otp = request.data.get('otp',None)
            email = request.data.get("email")
            phone = request.data.get("phone")
            
            if not director :
                return Response({"error": "Director not found"}, status=status.HTTP_200_OK)
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            if otp is  None   :
                # we will send otp to the user email
                if not email == user.email : # new email come 
                    invalid_email  = User.objects.filter(email = email ).exclude(id=user.id)
                    if invalid_email :
                        return Response({"error": "Email already exist"}, status=status.HTTP_200_OK)
                if not phone == user.phone_number : # new email come 
                    invalid_phone  = User.objects.filter(phone_number = phone ).exclude(id=user.id)
                    if invalid_phone :
                        return Response({"error": "Phone already exist"}, status=status.HTTP_200_OK)
                
                # send otp here 
                try:
                    # generate and send it  
                    generated_otp = generate_5_otp()
                    director.user.verificationcode.setCode(generated_otp)
                    director.user.save()
                    print('generated_otp: ', director.user.verificationcode.code)
                    html_content = generate_otp_email(director.user.username,generated_otp)
                    send_html_email.delay(
                        subject="🔐 Your EDUPORTAL OTP Code",
                        to_email = email,
                        html_content=html_content
                    )
                except : 
                    pass
                return Response ({
                    'success':'otp_sent',
                },status= status.HTTP_200_OK)
            
            # validate otp 
            if otp and not director.user.verificationcode.checkCode(otp):
                 return Response({
                    'error' : 'Invalid OTP ',
                },status=status.HTTP_200_OK)
                
            if otp and director.user.verificationcode.is_expired():
                 return Response({
                    'error' : 'otp has expired! ',
                },status=status.HTTP_200_OK)
            serializer = DirectorDetailSerializer(director,data=request.data, partial=True, context={"request":request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": "Profile updated successfully",
                    "updated_director": serializer.data
                }, status=status.HTTP_200_OK)

            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": str(e) }, status=status.HTTP_200_OK)

#==================================================================================================            
#                                       Director SETTINGS                           
#==================================================================================================

class DirectorSettingsView(APIView) :
    parser_classes =[MultiPartParser,FormParser]
    permission_classes=[
        permissions.IsAuthenticated,
        # DirectorUserPermission,
    ]
    
    def put(self, request, school_id) :
        try:
            # ============= required fields ==============
            user = request.user
            pin_set = True if request.data.get('requirePin') == 'true' else False
            otp_required = True if request.data.get('twoFactor')  == 'true' else False
            login_alerts = True if request.data.get('loginAlerts')  == 'true' else False
            session_timeout = request.data.get('sessionTimeout')
            

            
            # validate director actions 
            pin = request.data.get('pin')
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            school = School.objects.filter(id=school_id).first()  #.exists()
            if not school: 
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)
            
            user.pin_set = pin_set
            user.otp_required = otp_required
            user.login_alerts = login_alerts
            user.session_timeout = session_timeout
            user.save()
            # send the 
            try:    
                html_content = generate_school_update_email(
                    user.full_name() , 
                    school.name, 
                )
                send_html_email.delay(
                    subject="School Account Updated" ,
                    to_email=[user.email] , 
                    html_content=html_content
                )
            except Exception :
                    pass 
            data ={
                "requirePin":user.pin_set,
                "twoFactor":user.otp_required,
                "sessionTimeout":user.session_timeout,
                "loginAlerts":user.login_alerts,
            }
            return Response({"success":"user settings  updated successfully", "updated_user":data}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
  