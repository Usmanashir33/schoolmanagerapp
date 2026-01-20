
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from authUser.models import User
from django.core.mail import send_mail

from django.core.exceptions import ValidationError
from .models import  VerificationCode
import string
import random


# signals.py
@receiver(post_save, sender=User)
def create_verification(sender, instance, created, **kwargs):
    if created:
        verification=VerificationCode.objects.create(user=instance)
        verification.save() 
        
