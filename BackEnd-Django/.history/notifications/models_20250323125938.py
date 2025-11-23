from django.db import models
from account.models import User
import uuid

# Create your models here.

class Moneynotification(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Successful', 'Successful'),
        ('Failed', 'Failed'),
    ]

    TRANSACTION_TYPES = [
        # ('Airtime', 'Airtime'),
        # ('Data', 'Data'),
        # ('Electricity', 'Electricity'),
        ('Transfer-In', 'Transfer-In'),
        ('Transfer-Out', 'Transfer-Out'),
        ('Deposite', 'Deposite'),
        ('Withdraw', 'Withdraw'),
        ('Refund', 'Refund'),
    ]

    # id = models.AutoField(primary_key=True)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='moneynotifications')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    
    status = models.CharField(max_length=20,)
    transaction_type = models.CharField(max_length=50, )
    payment_type = models.CharField(max_length=50,blank=True)
    
    trx_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True)
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.transaction_type} - {self.status}"