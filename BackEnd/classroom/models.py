from django.db import models
# Create your models here.
from django.db import models
import shortuuid
from section.models import SchoolSection
from school.models  import  School ,Session 
from authUser.models import User
import os , uuid
from django.utils.translation import gettext_lazy as _  
from datetime import datetime
from director.models import Director
from core.models import  generate_unique_admission_number
from shortuuid.django_fields import ShortUUIDField

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'), 
)

# Create your models here.
class ClassRoom(models.Model): 
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)
    name = models.CharField(max_length=100)  # Example: "SS1 A"
    section = models.ForeignKey(SchoolSection, on_delete=models.CASCADE, related_name="classrooms", null=True,)
    # form_teacher = models.ForeignKey('teacher.Teacher', on_delete=models.CASCADE, related_name="formclasses", null=True,blank=True,)
    joined_at = models.DateTimeField(auto_now_add=True)
     
    def __str__(self):
        return f"{self.name} - {self.section.school.name}" 
    
class PromotionLog(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    # id = ShortUUIDField(
    #     length=12,
    #     max_length=12,
    #     primary_key=True,
    #     alphabet="abcdefghijklmnopqrstuvwxyz1234567890"
    # )
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="promotion_logs"
    )

    session = models.ForeignKey(
        Session,
        on_delete=models.SET_NULL,
        related_name="promotion_logs",
        null=True
    )

    promoted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_promotions"
    )

    total_students = models.PositiveIntegerField(
        default=0
    )

    promoted_students = models.PositiveIntegerField(
        default=0
    )

    skipped_students = models.PositiveIntegerField(
        default=0
    )

    failed_students = models.PositiveIntegerField(
        default=0
    )

    total_batches = models.PositiveIntegerField(
        default=1
    )

    processed_batches = models.PositiveIntegerField(
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    message = models.TextField(
        null=True,
        blank=True
    )

    mappings = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # updated_at = models.DateTimeField(
    #     auto_now=True
    # )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            # models.Index(fields=["school"]),
            models.Index(fields=["session"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return (
            f"{self.school} → "
            f"{self.status}"
            f"({self.session})"
        )