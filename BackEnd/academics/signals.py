
from django.core.cache import cache

from academics.models import ClassRoom, Subject,SchoolSection
from academics.models import ClassRoom
from student.models import Student, StudentClassEnrollment

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Student)
@receiver(post_delete, sender=Student)

@receiver(post_save, sender=Subject)
@receiver(post_delete, sender=Subject)

@receiver(post_save, sender=SchoolSection)
@receiver(post_delete, sender=SchoolSection)

def clear_academics_cache(sender, instance, **kwargs):
    cache.delete_pattern(
        f"academics_{instance.school.id}_*"
    )
    
@receiver(post_save, sender=ClassRoom)
@receiver(post_delete, sender=ClassRoom)
def clear_academics_cache(sender, instance, **kwargs):
    cache.delete_pattern(
        f"academics_{instance.section.school.id}_*"
    )
