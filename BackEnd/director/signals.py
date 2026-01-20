from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from authUser.models import User
from django.core.mail import send_mail

from django.core.exceptions import ValidationError
from .models import Director
import string
import random

def generate_random_password(length=8):
    """Generate a random password with letters and digits"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


# craete director 
@receiver(pre_save, sender=Director) 
def create_director_user(sender, instance, **kwargs):
    if not instance.user_id:
        if not instance.email:
            raise ValidationError("Director email is required to create a user.")
        # check if email is unique
        email = instance.email
        if User.objects.filter(email=email).exists():
            raise ValidationError(f"Email {email} already exists.")
        username = f"{instance.email.split('@')[0]}"

        user = User.objects.create(
            username=username,
            first_name=instance.first_name,
            last_name=instance.last_name,
            middle_name = instance.middle_name,
            email = instance.email,
            phone_number = instance.phone,
            role = instance.role,
            gender = instance.gender,
        ) 
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
