from django.db import models
from ac

# Create your models here.

class MoneyTransaction(models.Model):
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
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_charges = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50,blank=True)
    
    trx_id = models.CharField(_("Api Trx Id"), max_length=200,blank=True)
    trx_ref = models.CharField(max_length=100, blank=True, null=True)
    
    # metadata
    originator_name = models.CharField(max_length=100, blank=True, null=True)
    originator_bank = models.CharField(max_length=100, blank=True, null=True)
    originator_acc_num = models.CharField(max_length=100, blank=True, null=True)
    
    
    status = models.CharField(max_length=20,)
    transaction_type = models.CharField(max_length=50, )
    payment_type = models.CharField(max_length=50,blank=True)
    
    trx_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True)
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # # purchase 
    # customer_phone = models.CharField(max_length=15,blank=True)
    # network_provider = models.CharField(max_length=50,blank=True)
    # product = models.CharField(max_length=100,blank=True)
    
    # for transfer 
    receiver = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='Transfer_in',blank=True,null=True)
    
    # api_provider = models.CharField(max_length=100,blank=True)
    # response_message = models.TextField(blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.transaction_type} - {self.status}"