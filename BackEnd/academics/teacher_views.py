from django.db.models import Q, Count
from django.utils import timezone
from django.core.cache import cache

# views.py or any view file
from core.emails.email_templates.emails import generate_school_update_email,generate_school_delete_email
from core.formatters import format_serializer_errors
from core.tasks import send_html_email,send_ordinary_sms
from core.custom_pegination import CustomPagination50

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser

from student.models import Student, StudentClassEnrollment

from school.models import School,ActivityLog
from school.models import School,Session

from school.serializers import *
from school.models import School 
from school.permissions import HasSchoolPermission, SchoolPermissions
from school.tasks import SchoolServices


from .serializers import *
from .models import *
from .utils import ClassRoomServices
from .tasks import promote_students_task 

class TeacherAcademicDetailsView(APIView):
    # permission_classes = [HasSchoolPermission]
    # required_permissions = [SchoolPermissions.CAN_MANAGE_ACADEMICS] 
    
    def get(self, request,school_id,academic_item,item_id):   ## add new academic data
        try:
           
            valid_school = School.objects.filter( id=school_id).prefetch_related('sections', 'sections__classrooms','subjects__teaching_assignments').first()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            
            # find catched data before querying the database
            cache_key = f"academics_{school_id}_{academic_item}_{item_id}_by_{request.user.id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            
            #---------------------------SECTION -------------------
            if academic_item == "sections":
                section= valid_school.sections.filter(id=item_id).first()
                if not section :
                    return Response({"error": "Section not found"}, status=status.HTTP_200_OK)
                serializer = SchoolSectionDetailSerializer(section)
                resp = {
                    "success": "Section",
                    "section_details": serializer.data
                }
                try :
                    cache.set(cache_key,resp,timeout=60*5) # Cache for 5 minutes)
                except :
                    pass
                
                return Response(resp, status=status.HTTP_200_OK)
                    
            #--------------------------- CLASSROOM -------------------
            if academic_item == "classrooms" :
                classroom = ClassRoom.objects.filter(id=item_id,section__school__id = school_id).prefetch_related(
                    'student_enrollments__student','teaching_assignments'
                ).select_related(
                    'form_teacher'
                ).annotate(
                    studentsCount=Count(
                        "student_enrollments",
                        filter=Q(
                            student_enrollments__status__in=["active", "enrolled"]
                        ),
                        distinct=True,
                    ),
                    teachersCount=Count(
                        "teaching_assignments__teacher",
                        distinct=True,
                    ),
                ).first()
                if not classroom :
                    return Response({"error": "Classroom not found"}, status=status.HTTP_200_OK)
                serializer = ClassRoomDetailSerializer(classroom).data
                resp={
                    "success": "Classroom",
                    "classroom_details": serializer 
                }
                try :
                    cache.set(cache_key,resp,timeout=60*5) # Cache for 5 minutes)
                except :
                    pass
                
                return Response(resp, status=status.HTTP_200_OK)
            
            #---------------------------SUBJECTS -------------------
            if academic_item == "subjects":
                subject = valid_school.subjects.filter(id=item_id).first()
                if not subject :
                    return Response({"error": "Subject not found"}, status=status.HTTP_200_OK)
                serializer = SubjectDetailSerializer(subject)
                resp = {
                    "success": "Subject",
                    "subject_details": serializer.data
                }
                try :
                    cache.set(cache_key,resp,timeout=60*5) # Cache for 5 minutes)
                except :
                    pass
                
                return Response(resp, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
            
