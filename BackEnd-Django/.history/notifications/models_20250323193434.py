from django.db import models
from account.models import User
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.

class Notification(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='moneynotifications')
    title 
    date = models.DateTimeField(auto_now=True,blank=True)
    viewed = models.BooleanField(_("viewed"),default=False)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.transaction_type} - {self.status}"