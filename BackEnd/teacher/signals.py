from functools import cache

from django.db.models.signals import pre_save, post_save ,post_delete
from django.dispatch import receiver
from authUser.models import User
from django.core.mail import send_mail

from django.core.exceptions import ValidationError
from .models import Teacher 
from school.models import School,SchoolPermission, SchoolRole
import string
import random

def generate_random_password(length=8):
    """Generate a random password with letters and digits"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


@receiver(pre_save, sender=Teacher)
def create_teacher_user(sender, instance, **kwargs):
    if not instance.user_id:
        # check if email is unique
        email = instance.email
        username = instance.staff_id
        password = f"STAFF-{instance.email.split('@')[0]}"

        user = User.objects.create(
            username=username,
            school = instance.school ,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email = email,
            role = instance.role,
            gender = instance.gender
        )
        user.set_password(password)
        # get perfect role 
        # role = SchoolRole.objects.filter(school_id=instance.school.id, name="Teacher").first()
        # if role :
        #     user.school_role = role
        # user.save()
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

@receiver(post_delete, sender=Teacher)
def delete_user_when_student_deleted(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()
        
        
@receiver(post_save, sender=Teacher)
def update_user_when_student_updated(sender, instance, created, **kwargs):
    if not created : # that means its update 
        email = instance.email
        user = instance.user
        username = instance.staff_id
        
        user.first_name=instance.first_name 
        user.username = username 
        user.last_name=instance.last_name 
        user.middle_name=instance.middle_name 
        user.email=email 
        user.phone_number=instance.phone
        user.role = instance.role
        user.gender = instance.gender 
        user.save()

@receiver(post_save, sender=Teacher)
@receiver(post_delete, sender=Teacher)
def clear_teacher_cache(sender, instance, **kwargs):
    cache.delete_pattern(
        f"teachers_{instance.school.id}_*"
    )