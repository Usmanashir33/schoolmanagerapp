from django.db import models
from authUser.models import User
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from decimal import Decimal

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from shortuuid.django_fields import ShortUUIDField
import uuid

ACCOUNT_STATUS =(
    ("in-activa","inactive"),
    ("active","active"),
)
# Create your models here.
def user_directory_path(instance,filename) :
    ext = filename.split(".")[-1]
    filename = '%s_%s' % (instance.id,ext)
    return 'user_{0}/{1}'.format(instance.user.id,filename)


class Account(models.Model) :
    account_id = ShortUUIDField(unique=True,length=7,prefix="UAM",alphabet="1234567890",max_length =15,primary_key = True)
    user= models.OneToOneField(User, verbose_name=_("account_owner"), on_delete=models.CASCADE,related_name='account')
    account_balance = models.DecimalField(_("balance"), max_digits=15, decimal_places=2,default="0.00")
    date = models.DateTimeField(_("date_joined"),auto_now_add=True)
    account_status = models.CharField(_("status"),choices=ACCOUNT_STATUS,default='active',max_length=50)
    
    class Meta:
        ordering =['-date']
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        
    def current_account_number (self):
        return [x for x in self.accountnumbers.all()]
    
    def deposite(self,amount):
        new_bal = float(self.account_balance) + amount
        self.account_balance = new_bal
        self.save()
        
    def debit(self,amount):
        amount = float(self.account_balance) - amount
        self.account_balance = amount
        self.save()
        
    def __str__(self):
        return f"{self.account_id[:10]}..."
    
class AccountNumber(models.Model):
    account = models.ForeignKey(Account, verbose_name=_(""), on_delete=models.CASCADE,related_name='accountnumbers')
    account_number = models.CharField(_("Account Number"), max_length=50,editable=False)
    bank_name = models.CharField(_("Account Bank"), max_length=50,editable=False)
    flw_ref = models.CharField(_("creation ref"), max_length=50,editable=False)
    date_created = models.DateTimeField(_("date_joined"),auto_now_add=False)
    
    class Meta:
        ordering =['-date_created']
        verbose_name = _("Account Number")
        verbose_name_plural = _("Account Numbers")
        
    def __str__(self):
        return f"{self.account_number}"
    
class WithdrawalAccount(models.Model):
    account = models.ForeignKey(Account, verbose_name=_(""), on_delete=models.CASCADE,related_name='withdrawalaccounts')
    account_number = models.CharField(_("Account Number"), max_length=50,editable=False)
    account_name = models.CharField(_("Account Name"), max_length=50,editable=False)
    bank_name = models.CharField(_("Account Bank"), max_length=50,editable=False)
    bank_code = models.CharField(_("Account Code"), max_length=50,editable=False)
    is_default = models.BooleanField(_("is default"),default=False)
    date_created = models.DateTimeField(_("date_joined"),auto_now_add=True)
    
    class Meta:
        ordering =['-date_created']
        verbose_name = _("Withdrawal Account ")
        verbose_name_plural = _("Withdrawal Accounts ")
        
    def __str__(self):
        return f"{self.account_number}"

class MoneyTransaction(models.Model):
    STATUS_CHOICES = [ 
        ('pending', 'pending'),
        ('success', 'success'),
        ('failed', 'failed'),
    ]

    TRANSACTION_TYPES = [
        ('Airtime', 'Airtime'),
        ('Data', 'Data'),
        # ('Electricity', 'Electricity'),
        ('Transfer-In', 'Transfer-In'),
        ('Transfer-Out', 'Transfer-Out'),
        ('Deposite', 'Deposite'),
        ('Withdraw', 'Withdraw'),
        ('Refund', 'Refund'),
    ]
    
    # general info 
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_charges = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20,)
    notes = models.TextField(blank=True, null=True)
    transaction_type = models.CharField(max_length=50,)
    trx_date = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,blank=True,)
    
    api_trx_id = models.CharField(_("Api Trx Id"), max_length=200,blank=True)
    api_trx_ref = models.CharField(max_length=100, blank=True, null=True)
    
    # Deposite 
    depositor_name = models.CharField(max_length=100, blank=True, null=True)
    depositor_bank = models.CharField(max_length=100, blank=True, null=True)
    depositor_acc_num = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50,blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    payment_type = models.CharField(max_length=50,blank=True)
    
    # withdrawal
    withdrawal_account_number = models.CharField(max_length=50,blank=True)
    withdrawal_account_name = models.CharField(max_length=50,blank=True)
    withdrawal_bank_name = models.CharField(max_length=50,blank=True)
    withdrawal_bank_code = models.CharField(max_length=50,blank=True)
    
    # refund_etails
    refund_for = models.OneToOneField("self", verbose_name=_("refunded"), on_delete=models.DO_NOTHING ,null=True,blank=True) 
    
    # purchase details 
    phone_number = models.CharField(max_length=15,blank=True)
    network = models.CharField(max_length=50,blank=True)
    data_plane  = models.CharField(max_length=50,blank=True)
    
    # for internal transfers
    sender   = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='transfersout',blank=True,null=True) 
    receiver = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='transfersin',blank=True,null=True)
    approver = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='approvedtrx',blank=True,null=True)
    read_by_approver = models.BooleanField(_("read by approver"),default=False) 
    
    class Meta:
        ordering = ['-trx_date']
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
    
    
    def __str__(self):
        return f"{self.transaction_type} - {self.status}"

@receiver(post_save, sender=User)
def Account_post_save_receiver(sender,instance,created,**kwargs):
     if created :
        create_account = Account.objects.create(user=instance)
        create_account.save()
