
# core app
# views.py or any view file
from core.permissions import DirectorUserPermission

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from core.permissions import DirectorUserPermission
from core.custom_pegination import CustomPagination
from .models import Student
from classroom.models import ClassRoom
from school.models import School
from .serializers import StudentSerializer
