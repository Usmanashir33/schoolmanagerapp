import email
from django.core.exceptions import ValidationError

from django.utils import timezone
from django.db.models import Q
from rest_framework import serializers
from werkzeug import Response

from school.models import ActivityLog
from school.models import ActivityLog
from school.serializers import ActivityLogSerializer
import student
from .models import Student , StudentClassEnrollment
from academics.models import ClassRoom
from core.serializers import  ClassRoomSerializer
from core.websocketutils import signal_sender
from parent.models import Parents
from parent.serializers import ParentsSerializer
from authUser.serializers import MiniUserSerializer
from authUser.models import User
import json
from rest_framework import serializers
from school.tasks import SchoolServices

import json
from django.db import transaction

class StudentClassEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClassEnrollment  
        fields = '__all__'
        # read_only_fields = ['class_room',]
class StudentSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    guardian = ParentsSerializer(read_only=True) 
    class_rooms = StudentClassEnrollmentSerializer(many=True,read_only=True)
    active_class_rooms = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Student  
        fields = '__all__'
        read_only_fields = ['class_room',] 

    def get_active_class_rooms(self, obj):

        return list(
            StudentClassEnrollment.objects.filter(
                student=obj,
                status__in=["active", "enrolled"]
            ).values_list("class_room_id", flat=True)
        )

class StudentDetailFetchSerializer(serializers.ModelSerializer):
    class_room = ClassRoomSerializer(many=True)
    user = MiniUserSerializer(read_only=True)
    class Meta:
        model = Student
        fields = '__all__'
        extra_kwargs = {
        "class_room": {"required": False,}
    }
class MiniStudentSerializer(serializers.ModelSerializer): # for websocket 
    user = MiniUserSerializer(read_only=True)
    active_class_rooms = serializers.SerializerMethodField()
    def get_active_class_rooms(self, obj) : 
        # get enrollments for the student with only active or enrolled status and eturn the class ids 
        enrollments = StudentClassEnrollment.objects.filter(student=obj, status__in = ['active', 'enrolled'])
        return [enrollment.class_room.id for enrollment in enrollments]
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['id',]
class StudentDetailSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    picture = serializers.SerializerMethodField()
    guardian = ParentsSerializer(read_only=True)
    active_class_rooms = serializers.SerializerMethodField()
    class_rooms = StudentClassEnrollmentSerializer(  many=True,  read_only=True)
    class Meta:
        model = Student
        fields = "__all__"

    def get_active_class_rooms(self, obj):
        return [
            enrollment.class_room.id
            for enrollment in obj.class_rooms.all()
            if enrollment.status in ['active', 'enrolled']
        ]

    def get_picture(self, obj):
        return obj.picture.url if obj.picture else None
class StudentCreateSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    picture = serializers.SerializerMethodField(read_only=True)
    guardian = ParentsSerializer( read_only=True )
    active_class_rooms = serializers.SerializerMethodField(read_only=True)
    class_rooms = StudentClassEnrollmentSerializer( many=True, read_only=True)
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['guardian', 'id','class_room',]
        
    def get_active_class_rooms(self, obj) : 
        enrollments = StudentClassEnrollment.objects.filter(student=obj, status__in = ['active', 'enrolled'])
        return [enrollment.class_room.id for enrollment in enrollments]

    def get_picture(self, obj):
        return obj.picture.url if obj.picture else None 

    def create(self, validated_data):
        request = self.context['request']
        class_room_ids = request.data.getlist("class_rooms")
        guardian_data = request.data.get("guardian", None)
        picture_file = request.FILES.get("picture")

        # ✅ FIX: safe JSON parsing
        if guardian_data:
            try:
                guardian_data = json.loads(guardian_data)
            except (TypeError, ValueError):
                guardian_data = None

        with transaction.atomic():
            student = Student.objects.create(**validated_data)

            # ✅ FIX: picture must be saved 
            if picture_file:
                student.picture = picture_file
                student.save()

            if class_room_ids is not None :
                class_rooms = ClassRoom.objects.filter(id__in=class_room_ids).all()
                # loop through the  classes and created enrollment records  -
                for class_room in class_rooms:
                    StudentClassEnrollment.objects.create(
                        student=student,
                        class_room=class_room
                    )
            g_email = guardian_data.get('email','invalid') 
            g_full_name = guardian_data.get('full_name','invalid') 
            
            if guardian_data is not None and len(g_email)>8 and len(g_full_name)> 5 :
                parent = Parents.objects.filter(
                    Q(user__email__iexact = g_email.lower()) & Q(school=student.school) ).first()
                # if parent exit we just link it to the student if not we create new parent and link it to the student
                if not parent :
                    checking_user = User.objects.filter(email__iexact=g_email.lower()).first()
                    if checking_user :
                        raise ValidationError("A user with parent email already exists.")
                    parent = Parents.objects.create(
                        **guardian_data,
                        school=student.school
                    )
                student.guardian = parent
            student.save()

        return student

    def update(self, instance, validated_data):
        request = self.context['request']
        class_room_ids = request.data.getlist("class_room")
        guardian_data = request.data.get("guardian")
        picture_file = request.FILES.get("picture")

        # ✅ FIX: safe JSON parsing
        if guardian_data:
            try:
                guardian_data = json.loads(guardian_data)
            except (TypeError, ValueError):
                guardian_data = None

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            if picture_file:
                instance.picture = picture_file

            instance.save()

            if class_room_ids is not None:
                class_rooms = ClassRoom.objects.filter(id__in=class_room_ids)
                enrolleds = instance.class_rooms.all()
                for enrollment in enrolleds :
                    cls = enrollment.class_room
                    if cls  not in class_rooms :
                        enrollment.status = 'withdrawn'
                        enrollment.date_left = timezone.now()
                        enrollment.save()

                        
                # loop through the  classes and created enrollment records  -
                for class_room in class_rooms :
                    cls,created = StudentClassEnrollment.objects.get_or_create(
                        student=instance,
                        class_room=class_room
                    )
                    if not created and cls.status == 'withdrawn' :
                        cls.status = 'enrolled'
                        # cls.date_left = None
                        cls.date_joined = timezone.now()
                        cls.save()
                        
            g_email = guardian_data.get('email','invalid') 
            g_full_name = guardian_data.get('full_name',None) 
            
            if guardian_data is not None and len(g_email)>8 :
                if not g_full_name or len(g_full_name) < 5:
                    raise ValidationError("Guardian full name must be at least 5 characters long.")
                
                parent = Parents.objects.filter(Q(user__email__iexact = g_email.lower()) & Q(school=instance.school) ).first()
                # if parent exit we just link it to the student if not we create new parent and link it to the student
                if not parent :
                    checking_user = User.objects.filter(email__iexact=g_email.lower()).first()
                    if checking_user :
                        raise ValidationError("A user with parent email already exists.")
                    parent = Parents.objects.create(
                        **guardian_data, 
                        school=instance.school
                    )
                allowed_fields = [
                    "full_name", "phone", "gender",
                    "address", "relation_ship"
                ]

                for field in allowed_fields:
                    if field in guardian_data:
                        setattr(parent, field, guardian_data[field])
                instance.guardian = parent

            instance.save()
            # log the activity
            new_log = ActivityLog.objects.create(
                school = instance.school,
                user=request.user,
                action="UPDATE",
                module="STUDENT",
                description=f"Student updated: {instance.admission_number} - {instance.full_name()}"
            )
            # sendit to the user dashbord via websocket to update the student data in real time if the user is viewing the student list or the student details
            user_room = f"room{request.user.id}"
            log_data = ActivityLogSerializer(new_log).data
            data = {
                "type": "send_response1",
                "activity_log": log_data,
                }
            try:
                SchoolServices.send_activity_log.delay(destination=user_room, data=data)
            except :
                    pass
            
        return instance
