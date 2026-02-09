from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from authUser.models import User
from django.core.mail import send_mail

from django.core.exceptions import ValidationError
from .models import Parents
import string
import random

def generate_random_password(length=8):
    """Generate a random password with letters and digits"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

@receiver(post_save, sender=Parents)
def create_parents_user(sender, instance, **kwargs):
    if not instance.user_id:
        if not instance.email:
            raise ValidationError("Parent email is required to create a user.")

        if User.objects.filter(email=instance.email).exists():
            raise ValidationError(f"Email {instance.email} already exists.")

        names = instance.full_name.split()
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ""

        password = f"Parent-{instance.email.split('@')[0]}"
        username = instance.email.split('@')[0]

        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=instance.email,
            role=instance.role,
            gender=instance.gender
        )
        user.set_password(password)
        user.save()
        instance.user = user


@receiver(post_save, sender=Parents)
def update_parents_user(sender, instance, created, **kwargs):
    if not created:  # Only for updates
        user = instance.user
        if user:
            names = instance.full_name.split()
            first_name = names[0]
            last_name = names[1] if len(names) > 1 else ""

            user.username = instance.email.split('@')[0]  # derive from email
            user.first_name = first_name
            user.last_name = last_name
            user.email = instance.email
            user.role = instance.role
            user.gender = instance.gender
            user.save()
