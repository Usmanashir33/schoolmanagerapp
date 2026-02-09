from rest_framework import serializers
from .models import  Student
from classroom.models import ClassRoom
from core.serializers import  ClassRoomSerializer
from parent.models import Parents
from parent.serializers import ParentsSerializer
from authUser.serializers import MiniUserSerializer


class StudentSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    class Meta:
        model = Student  
        fields = '__all__'
        read_only_fields = ['class_room',]


class StudentDetailFetchSerializer(serializers.ModelSerializer):
    class_room = ClassRoomSerializer(many=True)
    user = MiniUserSerializer(read_only=True)
    class Meta:
        model = Student
        fields = '__all__'
        extra_kwargs = {
        "class_room": {"required": False,}
    }
import json
from rest_framework import serializers

import json
from django.db import transaction

class StudentDetailSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    picture = serializers.SerializerMethodField()
    guardian = ParentsSerializer(read_only=True)

    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['class_room', 'guardian', 'id']

    def get_picture(self, obj):
        return obj.picture.url if obj.picture else None
class StudentDetailSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    picture = serializers.SerializerMethodField()
    guardian = ParentsSerializer(read_only=True)

    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['class_room', 'guardian', 'id']

    def get_picture(self, obj):
        return obj.picture.url if obj.picture else None
class StudentDetailSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    picture = serializers.SerializerMethodField()
    guardian = ParentsSerializer(read_only=True)

    # ✅ FIX: explicitly mark class_room as read-only
    class_room = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['guardian', 'id','class_room']

    def get_picture(self, obj):
        return obj.picture.url if obj.picture else None

    def create(self, validated_data):
        request = self.context['request']
        class_room_ids = request.data.getlist("class_room")
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

            if class_room_ids:
                student.class_room.set(
                    ClassRoom.objects.filter(id__in=class_room_ids)
                )

            if guardian_data:
                parent = Parents.objects.filter(
                    email=guardian_data.get("email")
                ).first()

                if not parent:
                    parent = Parents.objects.create(**guardian_data)
                    parent.school = student.school
                    parent.save()

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

            if class_room_ids:
                instance.class_room.set(
                    ClassRoom.objects.filter(id__in=class_room_ids)
                )

            if guardian_data:
                parent = instance.guardian

                if not parent:
                    if guardian_data.get('email') and guardian_data.get('full_name'):
                        parent = Parents.objects.create(**guardian_data)
                        parent.school = instance.school
                        parent.save()
                        instance.guardian = parent
                else:
                    allowed_fields = [
                        "full_name", "phone", "gender",
                        "address", "relation_ship"
                    ]

                    for field in allowed_fields:
                        if field in guardian_data:
                            setattr(parent, field, guardian_data[field])

                    # ✅ FIX: save once, not in loop
                    parent.save()

            instance.save()

        return instance
