from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from authUser.models import User
from django.core.mail import send_mail

from django.core.exceptions import ValidationError
from .models import School
import string
import random

def generate_random_password(length=8):
    """Generate a random password with letters and digits"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

