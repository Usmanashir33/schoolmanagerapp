
from django.db.models.signals import pre_save, post_save ,pre_delete ,post_delete
from django.dispatch import receiver
from authUser.models import User
from django.core.mail import send_mail

from django.core.exceptions import ValidationError
from .models import Student
import string
import random

def generate_random_password(length=8):
    """Generate a random password with letters and digits"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

@receiver(pre_save, sender=Student)
def create_student_user(sender, instance, **kwargs):
    if not instance.user_id:
        if not instance.email:
            raise ValidationError("Student email is required to create a user.")
        # check if email is unique
        email = instance.email
        if User.objects.filter(email=email).exists():
            raise ValidationError(f"Email {email} already exists.")
        
        if not instance.admission_number:
            raise ValidationError("Student admission number is required to create a user.")
        
        username = instance.admission_number
        if User.objects.filter(username=username).exists():
            raise ValidationError(f"Username {username} already exists.")

        password = f"STU-{instance.email.split('@')[0]}"

        user = User.objects.create(
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
def update_user_when_student_updated(sender, instance, created, **kwargs):
    if not created : # that means its update 
        email = instance.email
        user = instance.user
        # check if email is unique
        if not user.email == email and User.objects.filter(email=email).exists() :
            # raise ValidationError(f"Email {email} already exists.")
            pass
        
        if not instance.admission_number:
            # raise ValidationError("Student admission number is required to update a user.")
            pass
        
        username = instance.admission_number
        if not user.username == username and User.objects.filter(username=username).exists():
            # raise ValidationError(f"Username {username} already exists.")
            pass
        
        user.first_name=instance.first_name 
        user.last_name=instance.last_name 
        user.middle_name=instance.middle_name 
        user.email=email 
        user.role = instance.role
        user.gender = instance.gender 
        user.save()
