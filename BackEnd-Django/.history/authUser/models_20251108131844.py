from django.db import models
import random ,os
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from shortuuid.django_fields import ShortUUIDField
import uuid
import shortuuid

# Create your models here. 
TRANSECTION_STATUS = (
    ("SUSP",'SUSPENDED'),
    ("NORM",'NORMAL')
)
ON_VERIFICATION_STATUS = ( 
    ("VERIFIED",'VERIFIED'),
    ("UNVERIFIED",'UNVERIFIED'),
    ("PENDING",'PENDING'),
)
def upload_user_image(instance,filename):
    ext = os.path.splitext(filename)[1]
    name = f"{instance.id}_pic{ext}"
    return os.path.join("users/",name)

class User(AbstractUser):
    id = models.UUIDField(_("id"),primary_key = True,unique=True,default = uuid.uuid4,editable=False)
    username = models.CharField(max_length=100)
    phone_number = models.CharField(_("phone_number"), max_length=14,blank=True,unique=True)
    email =models.EmailField(_("Email"),unique=True,max_length=254)
    picture= models.ImageField(_("user pic"), upload_to= upload_user_image,default='default.png')
    
    can_transect = models.BooleanField(_("can transect"),default=True)
    
    refarrel_code = models.CharField(
        _("invitation code"),
        max_length= 6,
        editable=False , blank = True
    )
    refarrels = models.ManyToManyField(
        "self", verbose_name=_("refarrels"),symmetrical=False,
        related_name='inviter',blank=True
    )
    kyc_submitted = models.CharField(
        _("kyc submitted"),max_length=50,
        choices=ON_VERIFICATION_STATUS,default='UNVERIFIED',
    ) 
    kyc_confirmed = models.BooleanField(_("kyc varified"),default=False)
    email_varified = models.BooleanField(_("varified email"),default=False)
    log_with_otp = models.BooleanField(_("login with otp"),default=True)
    lock_password = models.CharField(_("locking password"), max_length=6,blank=True)
    email_verification_code = models.CharField(_("email_verification_code"), max_length=255,blank=True)
    payment_pin = models.CharField(_("Payment Pin"), max_length=255,blank=True)
    payment_pin_set = models.BooleanField(_("Payment Pin Set"),default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default= False)
    is_active = models.BooleanField(_("active account"),default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) :
        return self.username
    
    def ID (self) :
        return  f"{str(self.id)[:6]}..."
    
    def setVerification
    
    def save(self, *args, **kwargs):
        if not self.refarrel_code:
            self.refarrel_code = self.generate_unique_referral_code()
        super().save(*args, **kwargs)

    def generate_unique_referral_code(self):
        alphabet = 'ABCDEFGHIJKLXZ123456789'
        while True:
            code = shortuuid.ShortUUID(alphabet=alphabet).random(length=6)
            if not User.objects.filter(refarrel_code=code).exists():
                return code




MEANS_OF_IDENTIFICATION = (
    ("national-id-card","National Id Card"),
    ("international-passport","International Passport"),
    ("driving-licence","Driving Licence"),
)
GENDER = (
    ("male","male"),
    ("female","female"),
    ("other","other"),
)
def upload_kyc_image(instance,filename) :
    ext = os.path.splitext(filename)[1]
    file_name = f"{instance.id}_file{ext}"
    folder= instance.user.username 
    return os.path.join(f"KYC",folder,file_name)

class KYC(models.Model):
    id = models.UUIDField(_("id"),primary_key = True,unique=True,default = uuid.uuid1,editable=False,)
    user = models.OneToOneField(User, verbose_name=_("account owner"), related_name='kyc',on_delete=models.CASCADE)
    full_name = models.CharField(_("Full Name "), max_length=100,blank=True)
    middle_name = models.CharField(_("middle Name "), max_length=100,blank=True)
    date_of_birth= models.DateField(_("DOB"), auto_now=False, auto_now_add=False)
    id_type = models.CharField(_("Id Type"), max_length=50,choices=MEANS_OF_IDENTIFICATION,default='national-id-card')
    id_number = models.CharField(_("Id Number "), max_length=70)
    
    address_pic = models.ImageField(_("id owner pic"), upload_to= upload_kyc_image ,null=True)
    user_pic= models.ImageField(_("id owner pic"), upload_to= upload_kyc_image ,null=True)
    id_card_pic= models.ImageField(_("id pic"), upload_to= upload_kyc_image ,null=True)
    signature_pic = models.ImageField(_("Signature"), upload_to=upload_kyc_image ,null=True)
    gender = models.CharField(_("gender"),choices=GENDER,max_length=50,null=True)
    
    # address 
    country = models.CharField(_("country"), max_length=50)
    city = models.CharField(_("city"), max_length=50,blank = True)
    state = models.CharField(_("state"), max_length=50)
    date = models.DateTimeField(_("date submitted"), auto_now_add=True)
    
    class Meta:
        ordering =['-date']
        verbose_name = _("KYC")
        verbose_name_plural = _("KYCs")

    def __str__(self):
        return f"kyc-{self.first_name}"

    # def get_absolute_url(self):
    #     return reverse("KYC_detail", kwargs={"pk": self.pk})

class StaffPins(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE,related_name='staffpins')
    pins = models.CharField(_("Action Pin"), max_length=255 ,blank=True)
    updated = models.DateTimeField(auto_now=True,)

    def __str__(self):
       return f"{self.user.username} staff Pin"

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'StaffPins'
        verbose_name_plural = 'StaffPins'