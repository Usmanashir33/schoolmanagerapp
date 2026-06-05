
from django.db.models.signals import pre_save, post_save ,pre_delete ,post_delete
from django.dispatch import receiver
from authUser.models import User
from django.core.mail import send_mail
from django.core.cache import cache
from parent.models  import Parents

from django.core.exceptions import ValidationError
from .models import Student,StudentClassEnrollment
import string
import random

def generate_random_password(length=8):
    """Generate a random password with letters and digits"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length)) 

@receiver(post_save, sender=Student)
def create_student_user(sender, instance, created , **kwargs):
    if created and  instance.email :
        email = instance.email
        username = instance.admission_number
        password = f"STU-{instance.email.split('@')[0]}"
        user = User.objects.create(
            school=instance.school,
            username=username,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=email,
            role = instance.role,
            gender = instance.gender
        )
        user.set_password(password)
        user.save()
        instance.user = user
        instance.save()

        # Send email with credentials
        # send_mail(
        #     subject='Your School Account',
        #     message=f"Hello {instance.first_name},\n\n"
        #             f"Your account has been created.\n"
        #             f"Username: {username}\n"
        #             f"Password: {password}\n\n"
        #             "Please log in and change your password.",
        #     from_email='noreply@yourschool.com',
        #     recipient_list=[instance.email],
        #     fail_silently=True  # Set to False for debugging
        # )
        
        
# ============================
# DELETE USER WHEN STUDENT DELETED
# ============================
@receiver(post_delete, sender=Student)
def delete_user_when_student_deleted(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()
        
@receiver(post_save, sender=Student)
def update_user_when_student_updated(sender, instance, created, **kwargs) :
    if not created :
        if instance.user and instance.email : # that means its update 
            email = instance.email
            user = instance.user
            username = instance.admission_number
            
            user.first_name=instance.first_name 
            user.last_name=instance.last_name 
            user.middle_name=instance.middle_name 
            user.email=email 
            user.username=username  
            user.role = instance.role
            user.gender = instance.gender 
            user.save()
        if not instance.user and instance.email : # that means user was not created before because email was not provided but now email is provided so we need to create user for the student
            user = User.objects.create(
                school=instance.school,
                username=instance.admission_number,
                first_name=instance.first_name,
                last_name=instance.last_name,
                email=instance.email,
                role = instance.role,
            )
            password = f"STU-{instance.email.split('@')[0]}"
            user.set_password(password)
            user.save()
            instance.user = user
            instance.save()

@receiver(post_save, sender=Student)
@receiver(post_delete, sender=Student)
def clear_student_cache(sender, instance, **kwargs):
    try :
        cache.delete_pattern(
            f"students_{instance.school.id}_*"
        )
        cache.delete(f"student_detail_{instance.school.id}_{instance.id}")
    except :
        pass
    
@receiver(post_save, sender=User)
@receiver(post_delete, sender=User)
@receiver(post_save, sender=Parents)
@receiver(post_delete, sender=Parents)
def clear_student_cache(sender, instance, **kwargs):
    try :
        cache.delete_pattern(
            f"students_{instance.school.id}_*"
        )
        cache.delete(f"student_detail_{instance.school.id}_{instance.student.id}")
    except :
        pass
    
@receiver(post_save, sender=StudentClassEnrollment)
@receiver(post_delete, sender=StudentClassEnrollment)
def clear_student_cache(sender, instance, **kwargs):
    try :
        cache.delete_pattern(
            f"students_{instance.school.id}_*"
        )
        cache.delete(f"student_detail_{instance.student.school.id}_{instance.student.id}")
    except :
        pass