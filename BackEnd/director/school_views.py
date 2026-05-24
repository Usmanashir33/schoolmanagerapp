from finance.models import *
from finance.serializers import SchoolFeeSerializer
from django.db.models import Prefetch,Q
from django.core.files.uploadedfile import UploadedFile
from core.emails.email_templates.emails import generate_school_update_email,generate_school_delete_email
from core.tasks import send_html_email,send_ordinary_sms

from core.permissions import DirectorUserPermission
from core.serializers import SchoolSerializer 
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from school.models import *
from academics.models import *
from academics.serializers import PromotionLogSerializer,SubjectSerializer
from teacher.models import *
from staff.models import *
from staff.serializers import StaffDetailSerializer
from student.serializers import StudentSerializer
from teacher.serializers import TeacherSerializer 

from school.models import *
from school.serializers import ActivityLogSerializer, FinanceSettingsSerializer, SchoolPermissionSerializer, SchoolRoleSerializer, TemplatesSerializer


#==================================================================================================            
#                                       SCHOOL  SECTION                           
#==================================================================================================

class DirectorSchoolDetailView(APIView) :
    parser_classes =[MultiPartParser,FormParser]
    permission_classes=[
        permissions.IsAuthenticated,
        DirectorUserPermission,
    ]
    def get(self, request,school_id): # get school data 
        try:
            school = School.objects.select_related("director").filter(id=school_id,director__user__id = request.user.id).first()
            if not school :
                return Response({"error":"school not found "},status=status.HTTP_200_OK)
            # limited to 100  recordes    per model to avoid overloading the response and client side
            school_data = School.objects.prefetch_related(
                    'finance',
                    "permissions",
                    Prefetch(
                        "roles",
                        queryset=SchoolRole.objects.exclude(name__exact = "Director").order_by("name")
                    ),
                    Prefetch(
                        "students",
                        queryset=Student.objects.order_by("joined_at")
                    ),
                    Prefetch(
                        "promotion_logs",
                        queryset=PromotionLog.objects.order_by("-created_at")
                    ),
                    Prefetch(
                        "teachers",
                        queryset=Teacher.objects.order_by("joined_at")
                    ),
                    Prefetch(
                        "staffs",
                        queryset=Staff.objects.order_by("joined_at")
                    ),
                    Prefetch(
                        "subjects",
                        queryset=Subject.objects.order_by("-added_at")
                    ),
                    Prefetch(
                        "templates",
                        queryset=Templates.objects.order_by("-created_at")
                    ),
                    Prefetch(
                        "class_fee_settings",
                        queryset=ClassFeeSetting.objects.order_by("-created_at")
                    ),
                    Prefetch(
                        "activity_logs",
                        queryset=ActivityLog.objects.filter(user_id = request.user.id).order_by("-created_at")
                    ),
                ).get(id=school.id)
            return Response({ 
                "success":'school_data', 
                "school_and_academics" : SchoolSerializer(school).data, 
                "school_students" : StudentSerializer(school_data.students.all()[:60],many=True).data , 
                "school_teachers" : TeacherSerializer(school_data.teachers.all()[:60],many=True).data ,
                "school_staffs"   : StaffDetailSerializer(school_data.staffs.all()[:60],many=True).data,
                "school_subjects" : SubjectSerializer(school_data.subjects,many=True).data,
                "templates" : (TemplatesSerializer(school_data.templates,many=True).data
                               if hasattr(school_data,'templates') else [] ),
                "promotion_logs" : (PromotionLogSerializer(school_data.promotion_logs.all()[:30],many=True).data
                               if hasattr(school_data,'promotion_logs') else [] ),
                "activity_logs" : (ActivityLogSerializer(school_data.activity_logs.all()[:100],many=True).data
                               if hasattr(school_data,'activity_logs') else [] ),
                "finance" : (FinanceSettingsSerializer(school_data.finance).data
                            if hasattr(school_data,'finance') else []),
                "class_fee_settings" : SchoolFeeSerializer(school_data.class_fee_settings,many=True).data,
                "school_permissions" : SchoolPermissionSerializer(school_data.permissions,many=True).data,
                "school_roles" : SchoolRoleSerializer(school_data.roles,many=True).data,
                }, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK)
        
    def put(self, request, school_id) :
        # try:
            director = request.user.director
            # ============= required fields ==============
            request_data = request.data.copy() 
            pin = request.data.get('pin')
            new_name = request.data.get('name')
            new_email = request.data.get('email')
            new_tag = request.data.get('tag')
            new_phone = request.data.get('phone')
            logo = request_data.get('logo',None)
            request_data.pop('picture',None) 
            # validate logo if file not path 
            if logo and not  isinstance(logo,UploadedFile) :
                request_data.pop('logo',None)
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            # validate director actions 
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school: 
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)
            
            existing_field = School.objects.filter(
                Q(name__iexact=new_name) |
                Q(email__iexact=new_email) |
                Q(phone__iexact=new_phone) |
                Q(tag__iexact=new_tag)
            ).exclude(id=school.id).first()
            if existing_field:

                if existing_field.name.lower() == new_name.lower():
                    return Response({"error": "Name already exists"})

                if existing_field.email.lower() == new_email.lower():
                    return Response({"error": "Email already exists"})

                if existing_field.phone.lower() == new_phone.lower():
                    return Response({"error": "Phone already exists"})

                if existing_field.tag.lower() == new_tag.lower():
                    return Response({"error": "Tag already exists"})
                        
            serializer = SchoolSerializer(school, data=request_data, context={"request":request} ,partial=True)
            if serializer.is_valid() : 
                serializer.save()  
                 # send the email to director
                try:    
                    html_content = generate_school_update_email(
                        school.director.full_name , 
                        school.name, 
                    )
                    send_html_email.delay(
                        subject="School Account Updated" ,
                        to_email=[school.director.email,school.email] , 
                        html_content=html_content
                    )
                except Exception :
                    pass 
                return Response({"success":"school updated successfully", "updated_school": serializer.data}, status=status.HTTP_200_OK)
            print(serializer.errors)
            return Response({'error': 'School update failed!'}, status=status.HTTP_200_OK)
        # except:
            # return Response({"error":"server error"},status=status.HTTP_200_OK)
    
    def post(self, request,school_id): # delting the school request 
        try:
            director = request.user.director
            
            # ============= required fields ==============
            pin = request.data.get('pin')
            reason  = request.data.get('reason')
            action = request.data.get("action")
            
            if action != "delete" :
                return Response({"error": "invalid action"}, status=status.HTTP_200_OK)
                
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
             # validate director actions 
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school:
                return Response({"error": "school not Found"}, status=status.HTTP_200_OK)
            
            # craete delte request here 
            if school.delete_requests :
                school.on_delete_request = True
                school.save()
                return Response({"success": "school delete in progress",
                                 "details" :f"R-{school.delete_requests.days_remain()}" }, status=status.HTTP_200_OK) 
            del_request = SchoolDeleteRequest.objects.create( 
                reason = reason, school = school
            )
            del_request.save() 
            # send the email to director
            try:    
                html_content = generate_school_delete_email(
                    school.director.full_name,
                    school.name,
                )
                send_html_email.delay(
                    subject="❌ School Account Delete Processing......",
                    to_email=[school.director.email,school.email],
                    html_content=html_content)
            except: 
                pass
            return Response({"success":"school delete request submitted successfully",'school': SchoolSerializer(school).data},status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
        
