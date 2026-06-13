
from django.db.models.signals import pre_save, post_save ,pre_delete ,post_delete
from django.dispatch import receiver
from authUser.models import User
from django.core.mail import send_mail
from django.core.cache import cache
from .models import StudentTransaction,PaymentInitiation

@receiver(post_save, sender=StudentTransaction)
@receiver(post_delete, sender=StudentTransaction)
def clear_student_cache(sender, instance, **kwargs):
    try :
        cache.delete_pattern(
            f"financedashbord_{instance.school.id}_*"
        )
        cache.delete_pattern(
            f"configured_classes_{instance.school.id}_*"
        )
        cache.delete_pattern(
            f"financedashbordstudenttrxs_{instance.school.id}_*"
        )
        cache.delete_pattern(
            
            f"studentLedger_{instance.school.id}_*"
        )
    except :
        pass

@receiver(post_save, sender=PaymentInitiation)
@receiver(post_delete, sender=PaymentInitiation)
def clear_payment_cache(sender, instance, **kwargs):
    try :
        cache.delete_pattern(
            f"paymentinit_{instance.school.id}_{instance.id}"
        )
        cache.delete_pattern(
            f"financedashbord_{instance.school.id}_*"
        )
        cache.delete_pattern(
            f"financedashbordstudenttrxs_{instance.school.id}_*"
        )
        cache.delete_pattern(
            f"pendingpayments_{instance.school.id}"
        )
        cache.delete_pattern(
            f"studentLedger_{instance.school.id}_*"
        )
    except :
        pass