from django.db.models.signals import pre_save, post_save,post_delete
from django.dispatch import receiver
from authUser.models import User
from django.core.mail import send_mail
from django.core.cache import cache

from .models import *

@receiver(post_save, sender=ResultBatch)
@receiver(post_delete, sender=ResultBatch)
def clear_dashboard_cache(sender, instance, **kwargs):
        try :
            cache_key = f"results_{instance.school.id}_*"
            cache.delete_pattern(cache_key)
            
            cache_key2 = f"result_{instance.session_id}_{instance.term_id}_{instance.class_id}_{instance.subject_id}_*"
            cache.delete_pattern(cache_key2)
            
        except :
            pass
@receiver(post_save, sender=CharacterBatch)
@receiver(post_delete, sender=CharacterBatch)
def clear_dashboard_cache(sender, instance, **kwargs):
        try :
            cache_key = f"charresults_{instance.school.id}_*"
            cache.delete_pattern(cache_key)
            
            cache_key3= f"skill_{instance.session_id}_{instance.term_id}_{instance.class_room_id}_*"
            cache.delete_pattern(cache_key3)
        except :
            pass
        
@receiver(post_save, sender=ApprovalRecord)
@receiver(post_delete, sender=ApprovalRecord)
def clear_dashboard_cache(sender, instance, **kwargs):
        try :
            cache_key = f"approvals_{instance.school.id}"
            cache.delete(cache_key)
        except :
            pass
        
@receiver(post_save, sender=ReportSheet)
@receiver(post_delete, sender=ReportSheet)
def clear_reportsheets_cache(sender, instance, **kwargs):
        try :
            cache_key = f"reportsheets_{instance.session_id}_{instance.term_id}_{instance.class_room_id}_*"
            cache.delete_pattern(cache_key)
            
            cache_key2 = f"reportsheet_{instance.session_id}_{instance.term_id}_{instance.class_room_id}_{instance.student_id}_*"
            cache.delete_pattern(cache_key2)
            cache_key2 = f"reportsheet_{instance.term_id}_{instance.class_room_id}_{instance.student_id}_*"
            cache.delete_pattern(cache_key2)
            
            cache_key2 = f"reportrecords_{instance.session_id}_{instance.term_id}_*"
            cache.delete_pattern(cache_key2)
        except :
            pass