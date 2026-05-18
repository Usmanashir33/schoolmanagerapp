import uuid,string,random

from django.db import models
from django.contrib.auth import get_user_model

from school.models import School

User = get_user_model()
def generate_device_code():
    random_part = ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=8)
    )
    return f"DEV-TAG-{random_part}"


class Device(models.Model):

    DEVICE_TYPES = (
        ("attendance", "Attendance"),
        ("security", "Security"),
        ("multi-purpose", "Multi Purpose"),
    )

    STATUSS = (
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("blocked", "Blocked"),
    )

    CONNECTIVITY = (
        ("online", "Online"),
        ("offline", "Offline"),
    )

    id = models.CharField(
        primary_key=True,
        max_length=255,
        editable=False,
        default=uuid.uuid4
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="devices",
        blank=True ,
        null=True 
    )

    name = models.CharField(max_length=150)

    purpose = models.TextField(blank=True, null=True)

    uniqueCode = models.CharField(
        max_length=255,
        unique=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUSS,
        default="active"
    )

    connectivity = models.CharField(
        max_length=20,
        choices=CONNECTIVITY,
        default="offline"
    )

    type = models.CharField(
        max_length=30,
        choices=DEVICE_TYPES,
        default="attendance"
    )

    location = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    lastSeen = models.DateTimeField(
        blank=True,
        null=True
    )

    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-createdAt"]
    def save(self, *args, **kwargs):

        if not self.uniqueCode:

            code = generate_device_code()

            while Device.objects.filter(uniqueCode=code).exists():
                code = generate_device_code()

            self.uniqueCode = code

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BiometricIdentity(models.Model):

    USER_TYPES = (
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("staff", "Staff"),
        ("director", "Director"),
    )

    id = models.CharField(
        primary_key=True,
        max_length = 255 ,
        editable=False,
        default=uuid.uuid4
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="biometric_identities",
        blank=True ,
        null=True 
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE ,
        related_name="biometric_identities"
    )

    userType = models.CharField(
        max_length=20,
        choices=USER_TYPES
    )

    faceData = models.JSONField(
        default=list
    )

    profileImage = models.ImageField(
        upload_to="biometric_profiles/",
        blank=True,
        null=True
    )

    createdAt = models.DateTimeField(auto_now_add=True)

    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-createdAt"]

    def __str__(self):
        return self.user


class AttendanceRecord(models.Model):

    ATTENDANCE_STATUS = (
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
    )

    id = models.CharField(
        primary_key=True,
        max_length = 255,
        editable=False,
        default=uuid.uuid4
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="attendance_records",
        blank=True ,
        null=True 
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="attendance_records"
    )

    status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS,
        default="present"
    )

    mode = models.CharField(
        max_length=50,
        default="face"
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    date = models.DateField()

    checkInTime = models.DateTimeField(
        blank=True,
        null=True
    )

    checkOutTime = models.DateTimeField(
        blank=True,
        null=True
    )

    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user} - {self.date}"