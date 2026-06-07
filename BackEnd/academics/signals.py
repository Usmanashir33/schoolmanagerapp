
from django.core.cache import cache

from academics.models import ClassRoom, Subject,SchoolSection,TeachingAssignment,PromotionLog
from student.models import Student, StudentClassEnrollment

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
    
@receiver(post_save, sender=TeachingAssignment)
@receiver(post_delete, sender=TeachingAssignment)

@receiver(post_save, sender=PromotionLog)
@receiver(post_delete, sender=PromotionLog)

@receiver(post_save, sender=Subject)
@receiver(post_delete, sender=Subject)

@receiver(post_save, sender=SchoolSection)
@receiver(post_delete, sender=SchoolSection)

def clear_academics_cache(sender, instance, **kwargs):
    try :
        cache.delete_pattern(
            f"academics_{instance.school.id}_*"
        )
    except :
        pass
    
@receiver(post_save, sender=ClassRoom)
@receiver(post_delete, sender=ClassRoom)
def clear_academics_cache(sender, instance, **kwargs):
    try :
        cache.delete_pattern(
            f"academics_{instance.section.school.id}_*"
        )
    except :
        pass
    
@receiver(post_save, sender=StudentClassEnrollment)
@receiver(post_delete, sender=StudentClassEnrollment)
def clear_academics_cache(sender, instance, **kwargs):
    try :
        cache.delete_pattern(
            f"academics_{instance.student.school.id}_*"
        )
    except :
        pass
