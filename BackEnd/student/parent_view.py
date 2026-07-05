
from django.db.models import Q
from core.formatters import format_serializer_errors
from core.permissions import ParentUserPermission
from school import permissions
# from core.permissions import DirectorUserPermission
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response

from .serializers import StudentDetailSerializer

from .models import Student
from django.utils import timezone

class ParentStudentDetailView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        ParentUserPermission,
    ]
    
    # ---------------- GET STUDENT DETAILS-----------------
    def get(self, request,school_id,student_id):  
        try: 
            cache_key = f"student_detail_{school_id}_{student_id}_{request.user.id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            valid_student  = Student.objects.filter(id = student_id,school__id=school_id,guardian__user=request.user).select_related(
                "user"
                ).prefetch_related(
                    "guardian",
                    "class_rooms"
                ).first()  #.exists()
            if not valid_student:
                return Response({"error": "Student not found"}, status=status.HTTP_200_OK)
            serializer = StudentDetailSerializer(valid_student)
            resp = {
                "success": "Student details",
                "student_details": serializer.data
            }
            try :
                cache.set(cache_key,resp,timeout=60*3)
            except:
                pass
            return Response(resp, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK )
