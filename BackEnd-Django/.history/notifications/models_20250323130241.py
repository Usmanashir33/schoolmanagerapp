from django.db import models
from account.models import User
import uuid

# Create your models here.

class Moneyotification(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='moneynotifications')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20,)
    transaction_type = models.CharField(max_length=50,)
    payment_type = models.CharField(max_length=50,blank=True)
    date = models.DateTimeField(auto_now=True,blank=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.status}"