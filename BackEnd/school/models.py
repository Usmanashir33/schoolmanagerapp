# Create your models here.
from django.db import models
import shortuuid
from authUser.models import User
import os , uuid
from django.utils.translation import gettext_lazy as _  
from datetime import datetime
from director.models import Director
from core.models import  generate_unique_admission_number
from django.utils import timezone

from django.db import models
from django.conf import settings
from shortuuid.django_fields import ShortUUIDField



def upload_school_picture(instance,filename):
    ext = os.path.splitext(filename)[1]
    name = f"{instance.id}_picture{ext}"
    return os.path.join("schools/",name)
def upload_school_logo(instance,filename):
    ext = os.path.splitext(filename)[1]
    name = f"{instance.id}_logo{ext}"
    return os.path.join("schools/",name)

def upload_staff_pic(instance,filename):
    ext = os.path.splitext(filename)[1]
    name = f"{instance.id}_logo{ext}"
    return os.path.join("staffs/",name)

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'), 
    ('other', 'Other'), 
)
GRADING_CHOICES = (
    ('standard', 'Standard (A-F)'),
    ('custom', 'Custom'),
)
class Term(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)
    school = models.ForeignKey('School', related_name='terms', blank=True, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=50)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name    
    
class Session(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)
    school = models.ForeignKey("School", related_name='sessions', on_delete=models.SET_NULL, blank=True, null=True)

    name = models.CharField(max_length=50)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) :
        return self.name
DEFAULT_MARKS ={
    'ca1':20,
    'ca2':20,
    'exam':60
}

def d_marks():
    return DEFAULT_MARKS.copy() 
class School(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)
    
    ref_id = models.CharField(max_length=20, unique=True, editable=False)
    director = models.ForeignKey(Director, on_delete=models.PROTECT,related_name='directorschools',blank=True, null=True)
    
    name = models.CharField(max_length=255,unique=True) 
    email = models.EmailField(_("email"), max_length=254,unique=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    logo = models.ImageField(upload_to=upload_school_logo,default='school_default.png', blank=True, null=True)
    tag = models.CharField(max_length=6, blank=True, null=True,unique=True)
    
    joined_at = models.DateTimeField(auto_now_add=True) 
    on_delete_request = models.BooleanField(default=False) 
    
    # academics 
    lock_records = models.BooleanField(default=False)
    grading_system = models.CharField(max_length=20, default='standard', choices=GRADING_CHOICES)
    auto_promotion = models.BooleanField(default=False)
    max_marks = models.JSONField(blank=True,null=True,default=d_marks)

    def save(self, *args, **kwargs):
        if not self.ref_id: 
            self.ref_id = self.generate_unique_sch_code('ref_id')
        super().save(*args, **kwargs)
        
    def generate_unique_sch_code(self, field, prefix='SCH'): 
        alphabet = 'QERTYUIOPASDFGHKLZXCVBNM12451234567890'
        while True:
            code = shortuuid.ShortUUID(alphabet=alphabet).random(length=11)  
            if not School.objects.filter(**{field: f"{prefix}-{code}"}).exists():
                return f"{prefix}-{code}"
        
    def __str__(self):
        return self.name
    
TEMPLATE_TYPE = (
    ("Form","Form"),
    ("Letter","Letter"),
    ("Report","Report"),
    ("Transcript","Transcript"),
    ("Certificate","Certificate"),
    ("Admission","Admission"),
    ("Other","Other") ,
)
    
# model to handle school templates 
class Templates(models.Model) :
    school = models.ForeignKey(School,on_delete=models.CASCADE,related_name = "templates")
    
    name = models .CharField(max_length= 100,)
    type = models .CharField(max_length= 100, choices=TEMPLATE_TYPE, default="Default")
    fileType = models .CharField(max_length= 100,blank=True)
    
    isConfigured = models .BooleanField(default=True)
    isActive = models.BooleanField( default=True )
    
    htmlContent = models.TextField(blank=True,null=True)
    config = models.JSONField(blank= True,null=True,default=dict)
    lastUpdated = models .DateTimeField( auto_now=True)
    created_at = models .DateTimeField(auto_now_add=True)
    
    
class SchoolDeleteRequest(models.Model) :
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)
    school = models.OneToOneField(School, on_delete=models.SET_NULL, related_name="delete_requests", null=True)
    reason = models.TextField()
    requested_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.school.on_delete_request = True
        self.school.save()
        super().save(*args, **kwargs)
    
    def days_remain(self):
        expiration_time = self.requested_at + timezone.timedelta(days=60)
        remaining_time = expiration_time - timezone.now()
        if remaining_time.total_seconds() <= 0:
            return 0
        return f"{remaining_time.days} days" 
    
    def __str__(self):
        return f"Delete Request for {self.school.name}"
class FinanceSettings(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)

    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name="finance")
    paymentDueDate = models.IntegerField(default=15)  
    onlinePayment = models.BooleanField(default=True) 
    
    def __str__(self):
        return f"Finance Settings for {self.school.name}"
class SchoolBankAccount(models.Model):
        id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)

        finance = models.ForeignKey(FinanceSettings, on_delete=models.CASCADE, related_name="bank_accounts")
        currency = models.CharField(max_length=10, default="NGN")
        bank_name = models.CharField(max_length=100)
        account_number = models.CharField(max_length=20)
        account_name = models.CharField(max_length=150)
        
        is_default = models.BooleanField(default=False)
        is_active = models.BooleanField(default=True)
        class Meta :
            unique_together = ('bank_name', 'account_number',"is_default")
        def __str__(self):
            return f"{self.finance.school.name} - {self.bank_name} ({self.account_number})"
        
class SchoolPermission(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="permissions")
    name = models.CharField(
        max_length=100,
        unique=True
    )
    description = models.CharField(
        max_length=255,
    )
    def __str__(self):
        return f"{self.school.name} - {self.name}"
    
class SchoolRole(models.Model) :
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length = 255)

    school = models.ForeignKey( 
        School,
        on_delete=models.CASCADE,
        related_name="roles"
    )
    name = models.CharField(
        max_length=100, 
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )
    permissions = models.ManyToManyField(SchoolPermission, related_name="roles", blank=True)
    def __str__(self):
        return self.name
class ActivityLog(models.Model):

    ACTION_CHOICES = [
        ("CREATE", "CREATE"),
        ("UPDATE", "UPDATE"), 
        ("DELETE", "DELETE"),
        ("SUSPEND", "SUSPEND"),
        ("LOGIN", "LOGIN"),
        ("PAYMENT", "PAYMENT") ,
    ]

    MODULE_CHOICES = [
        ("STUDENTS", "STUDENTS"),
        ("TEACHERS", "TEACHERS"),
        ("STAFF", "STAFF"),
        ("ACADEMICS", "ACADEMICS"),
        ("FINANCE", "FINANCE"),
        ("SETTINGS", "SETTINGS"),
        ("PROFILE", "PROFILE"),
        ("ROLES", "ROLES"),
        ("PERMISSIONS", "PERMISSIONS"),
    ]

    id = ShortUUIDField(
        length=12,
        max_length=20,
        primary_key=True,
        alphabet="abcdefghijklmnopqrstuvwxyz1234567890"
    )
    school = models.ForeignKey( 
        School,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_logs",
        db_index=True
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True
    )

    module = models.CharField(
        max_length=30,
        choices=MODULE_CHOICES,
        db_index=True
    )

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["module"]),
            models.Index(fields=["action"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.action}"