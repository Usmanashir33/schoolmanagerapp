from django.db import models
# Create your models here.
from django.db import models
import shortuuid
from school.models import School,Session
from authUser.models import User
from teacher.models import Teacher
import os , uuid
from django.utils.translation import gettext_lazy as _   
from core.models import  generate_unique_admission_number

#--------------------------------------------------------------------------------------
#                                    SECTION MODEL
#--------------------------------------------------------------------------------------
class SchoolSection(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)
    name = models.CharField(max_length=100,db_index=True) # Example: "SS1 A"
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sections") 
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.school.name}" 
    class Meta:
        db_table = 'section_schoolsection'
    

#--------------------------------------------------------------------------------------
#                                    CLASS SECTION 
#--------------------------------------------------------------------------------------

from django.utils.translation import gettext_lazy as _  
from shortuuid.django_fields import ShortUUIDField

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'), 
)

# Create your models here.
class ClassRoom(models.Model) : 
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)
    name = models.CharField(max_length=100,db_index=True)  # Example: "SS1 A"
    section = models.ForeignKey(SchoolSection, on_delete = models.SET_NULL, related_name="classrooms", null=True,)
    form_teacher = models.ForeignKey(Teacher, on_delete = models.SET_NULL, null=True, related_name="form_classes", blank=True)
    
    joined_at = models.DateTimeField(auto_now_add=True)
     
    def __str__(self):
        return f"{self.name} - {self.section.school.name}" 
    
    class Meta :
        db_table = 'classroom_classroom'
        
    
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

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = 'classroom_promotionlog'
        db_table = 'classroom_promotionlog'
        ordering = ["-created_at"]
        indexes = [
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

#--------------------------------------------------------------------------------------
#                                  SUBJECTS MODEL
#--------------------------------------------------------------------------------------
from school.models import School

# Create your models here.
class Subject(models.Model) :
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)
    school = models.ForeignKey(School,related_name="subjects", on_delete=models.CASCADE ,blank=True)
    name = models.CharField(max_length=100,db_index=True)
    code= models.CharField(max_length=20,null=True,db_index=True)   
    credits =models.IntegerField(blank=True,null=True)
    teachers = models.ManyToManyField(Teacher,related_name="subjects", blank=True,symmetrical=False,)
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta :
        db_table = 'subject_subject'
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name",'code']),
        ]
     
    def __str__(self):
        return self.school + " " + self.name + " " + self.code 
    
class TeachingAssignment(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="teaching_assignments"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="teaching_assignments"
    )

    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name="teaching_assignments"
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "teacher",
            "subject",
            "classroom",
        )
    def __str__(self):
        return f"{self.school.name} {self.teacher.full_name()} "
    