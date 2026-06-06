from django.core.cache import cache

from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from authUser.models import User
from django.core.mail import send_mail


from school.models import SchoolRole
from .models import Staff ,ActivityRole
import string
import random

def generate_random_password(length=8):
    """Generate a random password with letters and digits"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


@receiver(post_save, sender=Staff)
@receiver(post_delete, sender=Staff)
def clear_staff_cache(sender, instance, **kwargs):
    try : 
        cache.delete_pattern(
            f"staffs_{instance.school.id}_*"
        )
        cache.delete(f"staff_{instance.id}")
    except :
        pass
    
@receiver(post_save, sender=User)
@receiver(post_delete, sender=User)
def clear_staff_cache(sender, instance, **kwargs):
    try :
        cache.delete(f"staff_{instance.staff.id}")
    except :
        pass
    

@receiver(pre_save, sender=Staff)
def create_staff_user(sender, instance, **kwargs):
    if not instance.user_id:
        # check if email is unique
        email = instance.email
        username = instance.staff_id
        password = f"NAS-{instance.email.split('@')[0]}"

        user = User.objects.create(
            username=username,
            school = instance.school,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email = email,
            role = instance.role,
            gender = instance.gender
        )
        user.set_password(password)
        instance.user = user
        
@receiver(post_delete, sender=Staff)
def delete_user_when_staff_deleted(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()
        
@receiver(post_save, sender=Staff)
def update_user_when_staff_updated(sender, instance, created, **kwargs) :
    if not created :
        if instance.user and instance.email : # that means its update 
            email = instance.email
            user = instance.user
            username = instance.staff_id
            
            user.first_name=instance.first_name 
            user.last_name=instance.last_name 
            user.middle_name=instance.middle_name 
            user.email=email 
            user.username=username  
            user.role = instance.role
            user.gender = instance.gender 
            user.save()
        