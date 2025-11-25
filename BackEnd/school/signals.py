from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from authUser.models import User
from django.core.mail import send_mail

from django.core.exceptions import ValidationError
from .models import Student, Teacher ,Parents
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
            email=email
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

@receiver(pre_save, sender=Teacher)
def create_teacher_user(sender, instance, **kwargs):
    if not instance.user_id:
        if not instance.email:
            raise ValidationError("Teacher email is required to create a user.")
        if not instance.staff_id:
            raise ValidationError("Teacher staff number is required to create a user.")
        
        # check if email is unique
        email = instance.email
        if User.objects.filter(email=email).exists():
            raise ValidationError(f"Email {email} already exists.")
        
        username = instance.staff_id
        if User.objects.filter(username=username).exists():
            raise ValidationError(f"Username {username} already exists.")

        password = f"STAFF-{instance.email.split('@')[0]}"

        user = User.objects.create(
            username=username,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email = email
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
        #     fail_silently=True
        # )
@receiver(pre_save, sender=Parents)
def create_parents_user(sender, instance, **kwargs):
    if not instance.user_id:
        if not instance.email:
            raise ValidationError("Parents email is required to create a user.")
        
        # check if email is unique
        email = instance.email
        if User.objects.filter(email=email).exists():
            raise ValidationError(f"Email {email} already exists.")
        
        

        password = f"Parent-{instance.email.split('@')[0]}"
        username = f"{instance.email.split('@')[0]}"

        user = User.objects.create(
            username=username,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email = email
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
        #     fail_silently=True
        # )
