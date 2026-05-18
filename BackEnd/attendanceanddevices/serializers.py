from rest_framework import serializers

from .models import (
    Device,
    BiometricIdentity,
    AttendanceRecord
)


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = "__all__"


class BiometricIdentitySerializer(serializers.ModelSerializer):

    class Meta:
        model = BiometricIdentity
        fields = "__all__"


class UpdateBiometricIdentitySerializer(serializers.ModelSerializer):

    class Meta:
        model = BiometricIdentity
        fields = "__all__"
        read_only_fields = [
            "school",
            "user",
            "createdAt"
        ]


class AttendanceRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendanceRecord
        fields = "__all__"