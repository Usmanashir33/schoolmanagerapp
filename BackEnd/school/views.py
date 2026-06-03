# from logging import raiseExceptions
from datetime import timedelta
from django.utils import timezone 
from django.db import transaction
from django.db.models import Q
from django.core.cache import cache

# core app
# views.py or any view file
from core.custom_pegination import CustomPagination15
from core.custom_pegination import CustomPagination15
from core.emails.email_templates.emails import generate_otp_email,generate_login_email,generate_registration_email
from core.emails.email_templates.emails import generate_school_update_email,generate_school_delete_email
from core.tasks import send_html_email,send_ordinary_sms

from core.permissions import DirectorUserPermission
from core.formatters import format_serializer_errors


from core.serializers import SchoolSerializer,DirectorSerializer
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser

from school.permissions import HasSchoolPermission,SchoolPermissions
from .models import  ActivityLog, FinanceSettings, School ,SchoolDeleteRequest, SchoolRole,SchoolPermission
from .serializers import ActivityLogSerializer, SchoolBankAccountSerializer, SchoolPermissionSerializer, SchoolPermissionSerializer, SchoolRoleSerializer, TemplatesSerializer
from director.models import Director 
from authUser.models import User,PendingEmail
from authUser.serializers import MiniUserSerializer
from authUser.views import create_jwt_tokens_for_user ,serialize_with_role 
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
            director_gender = request.data.get('director_gender').lower()
            
            
            director_password = request.data.get('director_password')
            director_password2 = request.data.get('director_password2')

            # check if school or director email/phone  is used or any other unique field 
            school_exists = School.objects.filter(
                Q(email__iexact=email) |
                Q(phone__iexact=phone) |
                Q(tag__iexact=tag) |
                Q(name__iexact=name)
            ).values(
                "email",
                "phone",
                "tag",
                "name"
            ).first()

            if school_exists:
                if school_exists.get("email", "").lower() == email.lower():
                    return Response(
                        {"error": "school email already used!"},
                        status=status.HTTP_200_OK
                    )

                if school_exists.get("phone", "").lower() == phone.lower():
                    return Response(
                        {"error": "school phone already used!"},
                        status=status.HTTP_200_OK
                    )

                if school_exists.get("tag", "").lower() == tag.lower():
                    return Response(
                        {"error": "school tag already used!"},
                        status=status.HTTP_200_OK
                    )

                if school_exists.get("name", "").lower() == name.lower():
                    return Response(
                        {"error": "school name already used!"},
                        status=status.HTTP_200_OK
                    )
            user_exists = User.objects.filter(
                Q(email__iexact = director_email) | 
                Q(phone_number__iexact=director_phone)
                ).values(
                    "email",
                    "phone_number"
                ).first()

            if user_exists:
                if user_exists.get("email", "").lower() == director_email.lower():
                    return Response(
                        {"error": "director email is already used!"},
                        status=status.HTTP_200_OK
                    )

                if user_exists.get("phone_number", "").lower() == director_phone.lower():
                    return Response(
                        {"error": "director phone number is already used!"},
                        status=status.HTTP_200_OK
                    )
            # check paswords match - and greater than 7 
            if not director_password == director_password2 :
                return Response({"error":"invalid director password match"},status=status.HTTP_200_OK)
            if len(director_password) < 7 :
                return Response({"error":"director password too short"},status=status.HTTP_200_OK)
            
            if director_password in ['12345678','87654321','112233445','11111111','222222222','33333333','444444444','000000000'] :
                return Response({"error":"Week password(very common)!!!"},status=status.HTTP_200_OK)
            
            # check if pending email exist create the pending email verification for director
            
            # check if its first request we need to send otp
            if not verification_code : # send verification code 
                verification_code_gen = generate_5_otp() 
                
                # set new code and save
                pending_email, created  = PendingEmail.objects.get_or_create(email = director_email)
                pending_email.setCode(verification_code_gen)
                
                print(verification_code_gen,"Generated OTP for",director_email)
                
                #we send email with email_verification_code to directors Email 
                #send email here 
                try:
                    html_content = generate_otp_email(director_email,verification_code_gen )
                    send_html_email.delay (
                        subject="🔐 New registration OTP Code 10Min ",
                        to_email=director_email,
                        html_content=html_content
                    )
                except :
                    pass
                return Response({"success":f"OTP sent to {director_email}","otp_sent":True},status=status.HTTP_200_OK) 
            
            #-------------- if with otp check the OTP and create new school --------------------
            
            pending_email = PendingEmail.objects.filter(email = director_email)
            
            if not pending_email.exists() :
                return Response({"error":"initiate registration process"},status=status.HTTP_200_OK)
            
            #pending email exists continue processing 
            found_email = pending_email.first()
            if found_email.is_expired() :
                found_email.delete()
                return Response({"error":"expired!. Initiate registration process"},status=status.HTTP_200_OK)
            if not found_email.checkCode(verification_code) :
                return Response({"error":"invalid  verification code"},status=status.HTTP_200_OK)
            
            # every thing is ohk # create school  and director user
            with transaction.atomic() :
                director_data={
                    'first_name': director_first_name,
                    'last_name': director_last_name,
                    'middle_name': director_middle_name,
                    'email': director_email,
                    'phone': director_phone,
                    'title':director_title,
                    'gender':director_gender,
                    'role':'Director',
                }
                new_director = DirectorSerializer(data=director_data)
                user_data = {
                    "first_name": director_data["first_name"],
                    "last_name": director_data["last_name"],
                    "middle_name": director_data["middle_name"],
                    "phone_number": director_data["phone"],
                    "email": director_data["email"],
                    "username": director_data["email"].split("@")[0],
                    "email_verified": True,
                }
                new_user = MiniUserSerializer(data=user_data)
                serializer = SchoolSerializer(data={
                    'name': name,
                    'tag': tag ,
                    'phone': phone ,
                    'address': address ,
                    'email': email ,
                })
                if serializer.is_valid() and new_director.is_valid() and new_user.is_valid() :   
                #   create user, director, and school here 
                    user = new_user.save()
                    user.set_password(director_password)
                    user.email_varified = True
                    user.save() 
                    
                    director = new_director.save()
                    director.user = user 
                    director.save()
                    
                    school = serializer.save()
                    school.director = director
                    school.save()
                    
                    # attach director with all permissions 
                    director_role = SchoolRole.objects.filter(school=school, name="Director").first()
                    director_role.permissions.set(
                        school.permissions.all()
                    )
                    user.school_role = director_role
                    user.save()
                    
                    found_email.delete() # delete pending email after verification
                    
                    # send success email to director
                    try:    
                        html_content = generate_registration_email(
                                director_email,
                                f"{director.full_name()}({school.name})",
                            )
                        send_html_email.delay(
                            subject="✅ Director&School Account Created!",
                            to_email=[director_email, school.email ],
                            html_content=html_content
                        )
                    except:
                        pass
                    # generate this user access tokens 
                    tokens = create_jwt_tokens_for_user(director.user)
                    data = serialize_with_role(director.user,director.user.role) 
                    return Response({
                        "success":"School Registered Successfully ",
                        "school_created":{'role':director.role,"data":data, "tokens": tokens}
                        },status=status.HTTP_201_CREATED)
                else :
                    return Response({"error":"invalid details "},status=status.HTTP_200_OK)
        except :
           return Response({"error":"server error"},status=status.HTTP_200_OK)
       
class AllUserLogsView(APIView): #paginated request
    # permission_classes = [HasSchoolPermission]
    # required_permissions = [SchoolPermissions.CAN_VIEW_STAFFS]
    
    # ---------------- GET  ALL User Logs -----------------
    def get(self, request,school_id):  
        try:
            # get all User Logs of the school
            page = request.query_params.get("page", 1)
            cache_key = f"activity_{request.user.id}_{school_id}_page_{page}"
            cached_response = cache.get(cache_key)
            
            if cached_response:
                return Response(cached_response, status=status.HTTP_200_OK)
            logs  = ActivityLog.objects.filter(school_id = school_id,user__id = request.user.id)
            paginator =     CustomPagination15()
            paginated_logs = paginator.paginate_queryset(
                logs,
                request
            )

            serializer =    ActivityLogSerializer(
                paginated_logs,
                many=True
            ).data

            resp=paginator.get_paginated_response({
                "success": "School Users Logs", 
                "paginated_data": serializer
            })
            cache.set(cache_key,resp,timeout=60*5) # Cache for 5 minutes)
            return Response(resp, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

class SchoolRoleView(APIView) :
    permission_classes=[HasSchoolPermission]
    permissions_required = [
        SchoolPermissions.CAN_MANAGE_SCHOOL
    ]
    def post(self, request) :
        try:
            pin = request.data.get('pin')
            school_id = request.data.get("school")
            role_name = request.data.get("name")
            perm_ids = request.data.get("permissionIds")
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            school = School.objects.filter(id=school_id).prefetch_related("roles").first() 
            if not school: 
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)
            # validate no permission exist with this name 
            existed_perm = school.roles.filter(name__exact = role_name).first()
            if existed_perm :
                return Response({"error": "Role with this name already exist"}, status=status.HTTP_200_OK)
            # create new permission 
            find_perms = school.permissions.filter(id__in = perm_ids)
            if len(find_perms) != len(perm_ids) :
                return Response({"error": "One or more invalid permission ids"}, status=status.HTTP_200_OK)
            
            new_role = SchoolRoleSerializer(data=request.data,context = {"request":request,'perms':find_perms})
            if new_role.is_valid() :
                new_role.save()
                data = new_role.data 
                return Response({"success":"New Role Created ","new_role":data}, status=status.HTTP_200_OK)
            return Response({"error":"invalid details "},status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
        
    def put(self, request,role_id) :
        try:
            pin = request.data.get('pin')
            school_id = request.data.get("school")
            role_name = request.data.get("name")
            perm_ids = request.data.get("permissionIds")
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            school = School.objects.filter(id=school_id).prefetch_related("roles").first() 
            if not school: 
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)
            
            # find the role  and prevent director edition 
            role = school.roles.filter(id=role_id).first()
            if not role or role.name.lower() == "director":
                return Response({"error": "Role not found!"}, status=status.HTTP_200_OK)
            
            # validate no permission exist with this name 
            existed_role = school.roles.filter(name__exact = role_name).exclude(id=role_id).first()
            if existed_role :
                return Response({"error": "Role with this name already exist"}, status=status.HTTP_200_OK)
            
            # check available permission 
            find_perms = school.permissions.filter(id__in = perm_ids)
            if len(find_perms) != len(perm_ids) :
                return Response({"error": "One or more invalid permission ids"}, status=status.HTTP_200_OK)
            
            updated_role = SchoolRoleSerializer(role,data=request.data,context = {"request":request,'perms':find_perms})
            if updated_role.is_valid() : 
                updated_role.save()
                data = updated_role.data 
                return Response({"success":"Role Updated Succefully! ","updated_role":data}, status=status.HTTP_200_OK)
            return Response({"error":"invalid details "},status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
class SchoolPermsionView(APIView) :
    permission_classes=[HasSchoolPermission]
    permissions_required = [
        SchoolPermissions.CAN_MANAGE_SCHOOL
    ]
    def post(self, request) :
        try:
            pin = request.data.get('pin')
            school_id = request.data.get("school")
            perm_name = request.data.get("name")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            school = School.objects.filter(id=school_id).prefetch_related("permissions").first() 
            if not school: 
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)
            # validate no permission exist with this name 
            existed_perm = school.permissions.filter(name__exact = perm_name).first()
            if existed_perm :
                return Response({"error": "Permission with this name already exist"}, status=status.HTTP_200_OK)
            # create new permission 
            new_perm = SchoolPermissionSerializer(data=request.data)
            if new_perm.is_valid():
                new_perm.save()
                data = new_perm.data
                return Response({"success":"New Permission Created ","new_perm":data}, status=status.HTTP_200_OK)
            return Response({"error":"invalid details "},status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
    def put(self, request,perm_id) :
        try:
            pin = request.data.get('pin')
            school_id = request.data.get("school")
            perm_name = request.data.get("name")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            school = School.objects.filter(id=school_id).prefetch_related("permissions").first() 
            if not school: 
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)
            
            perm = school.permissions.filter(id=perm_id).first()
            if not perm :
                return Response({"error": "Permission not found"}, status=status.HTTP_200_OK)
            
            # validate no permission exist with this name 
            existed_perm = school.permissions.filter(name__exact = perm_name).exclude(id=perm_id).first()
            if existed_perm :
                return Response({"error": "Permission with this name already exist"}, status=status.HTTP_200_OK)
            # create new permission 
            new_perm = SchoolPermissionSerializer(perm, data=request.data)
            if new_perm.is_valid() :
                new_perm.save()
                data = new_perm.data
                return Response({"success":"Permission Updated ","updated_perm":data}, status=status.HTTP_200_OK)
            return Response({"error":"invalid details "},status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
class SchoolTemplateView(APIView) :
    parser_classes =[MultiPartParser,FormParser]
    permission_classes=[
        permissions.IsAuthenticated,
        DirectorUserPermission,
    ]
    
    def post(self, request, school_id) :
        try:
            director = request.user.director
            # validate director actions 
            pin = request.data.get('pin')
            print('request.data: ', request.data.get("isActive"))
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school: 
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)
            
            serializer = TemplatesSerializer(data=request.data )
            # by checking  directord pin 
            if serializer.is_valid() : 
                serializer.save()
                return Response({"success":"New Template Created&Activated ","new_temp":serializer.data}, status=status.HTTP_200_OK)
            return Response({"error":format_serializer_errors(serializer.errors)},status=status.HTTP_200_OK) 
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
    
    def put(self, request, school_id,template_id) :
        try:
            director = request.user.director
            # validate director actions 
            pin = request.data.get('pin')
            temp_activation_signal = True if  request.data.get("isActive",None) == True else False
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            school = School.objects.filter(director_id = director.id, id=school_id).first() #.exists()
            if not school: 
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)
            template = school.templates.filter(id=template_id).first()
            if not template: 
                return Response({"error": "Invalid Template"}, status=status.HTTP_200_OK)
            serializer = TemplatesSerializer(template,data = request.data ,partial=True)
            sameTemplates = school.templates.filter(
                    type = serializer.instance.type
                ).exclude(
                    id = serializer.instance.id
                )
            # by checking  directord pins
            if serializer.is_valid() : 
                serializer.save()
                # make the remaining ones inactives if one is set to active 
                if temp_activation_signal and len(sameTemplates) :
                    for s in sameTemplates : 
                        s.isActive = False
                        s.save()
                return Response({"success": "Template Updated","updated_temp":serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
    
    def delete(self, request, school_id,template_id,pin) :
        try:
            director = request.user.director
            # validate director actions 
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school: 
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)
            template = school.templates.filter(id=template_id).first()
            if not template: 
                return Response({"error": "Invalid Template"}, status=status.HTTP_200_OK)

            template.delete()
            return Response({"success": "Template Deleted","deleted_temp":{"id":int(template_id),"type":template.type}}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
    
    def get(self, request, school_id,template_id) :
        try:
            director = request.user.director
            # validate director actions 
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school: 
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)
            template = school.templates.filter(id = template_id).first()
            serializer = TemplatesSerializer(template,many=True)
            # by checking  directord pin 
            if serializer.is_valid() : 
                serializer.save()
                return Response({"template":serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
        
class SchoolFinanceView(APIView) :
    permission_classes=[
        permissions.IsAuthenticated,
        DirectorUserPermission,
    ]
    
    def post(self, request) :
        try:
            # validate director actions 
            director = request.user.director
            pin = request.data.get('pin')
            school_id = request.data.get("school")
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school : 
                return Response({"error": "Invalid school data"}, status=status.HTTP_200_OK)
            finance = FinanceSettings.objects.get_or_create(school=school)[0]
            if not finance: 
                return Response({"error": "Finance not configured yet "}, status=status.HTTP_200_OK)
            
            serializer = SchoolBankAccountSerializer(data=request.data,context = {"finance": school.finance} )
            if serializer.is_valid() : 
                serializer.save()
                return Response({"success":"New Bank Account Created","created_account":serializer.data}, status=status.HTTP_200_OK)
            return Response({"error":format_serializer_errors(serializer.errors)},status=status.HTTP_200_OK) 
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
    
    def put(self, request,acc_id) :
        try:
            # validate director actions 
            director = request.user.director
            pin = request.data.get('pin')
            school_id = request.data.get("school")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school: 
                return Response({"error": "Invalid school data"}, status=status.HTTP_200_OK)
            
            account = school.finance.bank_accounts.filter(id=acc_id).first()  #.exists()
            if not account: 
                return Response({"error": "Invalid account data"}, status=status.HTTP_200_OK)
                
            serializer = SchoolBankAccountSerializer(account,data = request.data ,partial=True)
           
            if serializer.is_valid() : 
                serializer.save()
                return Response({"success": "Bank Account Updated","updated_account":serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
    
    def delete(self, request,school_id,acc_id,pin) :
        try:
            director = request.user.director
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school: 
                return Response({"error": "Invalid school data"}, status=status.HTTP_200_OK)
            
            account = school.finance.bank_accounts.all().filter(id=acc_id)  #.exists()
            if not account.exists(): 
                return Response({"error": "Invalid account data"}, status=status.HTTP_200_OK)
                
            account.first().delete()
            return Response({"success": "Bank Account Deleted","deleted_account":{"id":acc_id}}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
    
    def get(self, request, school_id,template_id) :
        try:
            director = request.user.director
            # validate director actions 
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school: 
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)
            template = school.templates.filter(id = template_id).first()
            serializer = TemplatesSerializer(template,many=True)
            # by checking  directord pin 
            if serializer.is_valid() : 
                serializer.save()
                return Response({"template":serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
