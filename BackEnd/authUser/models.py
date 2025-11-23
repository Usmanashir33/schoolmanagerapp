from django.db import models
import random ,os
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from shortuuid.django_fields import ShortUUIDField
from django.contrib.auth.hashers import make_password, check_password

import uuid
import shortuuid

# Create your models here. 
TRANSECTION_STATUS = (
    ("SUSPENDED",'SUSPENDED'),
    ("NORMAL",'NORMAL')
)
VERIFICATION_STATUS = ( 
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
    middle_name = models.CharField(_("middle Name "), max_length=100,blank=True)
    # phone_number = models.CharField(_("phone_number"), max_length=14,blank=True,unique=True)
    phone_number = models.CharField(_("phone_number"), max_length=14,blank=True)
    email =models.EmailField(_("Email"),unique=True,max_length=254)
    picture= models.ImageField(_("user pic"), upload_to= upload_user_image,default='default.png')
    
    
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
        choices=VERIFICATION_STATUS,default='UNVERIFIED',
    ) 
    kyc_confirmed = models.BooleanField(_("kyc varified"),default=False)
    email_varified = models.BooleanField(_("varified email"),default=False)
    
    # security
    verification_code_set = models.CharField(_("verification_code"), max_length=255,blank=True)
    pin_set = models.BooleanField(_("Payment Pin Set"),default=False)
    
    # limitations 
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default= False)
    is_active = models.BooleanField(_("active account"),default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta :
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) :
        return self.username
    
    def show_id(self) :   
        return  f"{str(self.id)[:6]}..."
    
    # handle the verification code sent to the email 
    def setVerificationCode(self,row_pin):
        self.email_verification_code = make_password(str(row_pin))
        self.save()
        
    def checkVerificationCode(self,row_pin):
        return check_password(row_pin,self.email_verification_code)
    
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
    ("national_id","National Id Card"),
    ("passport","International Passport"),
    ("driving_licence","Driving Licence"),
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
    date_of_birth= models.DateField(_("DOB"), auto_now=False, auto_now_add=False)
    id_type = models.CharField(_("Id Type"), max_length=50,choices=MEANS_OF_IDENTIFICATION,default='national_id')
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

class UserPins(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE,related_name='userpins')
    pins = models.CharField(_("Pins"), max_length=255 ,blank=True)
    updated = models.DateTimeField(auto_now=True,)
    
    # this handles payment pin 
    def setPin(self,row_pin):
        self.pins = make_password(str(row_pin))
        self.save()
        
    def checkPin(self,row_pin):
        return check_password(str(row_pin),self.pins)

    def show_pins(self):
         return f"{self.pins[:6]}*****{self.pins[-6:]}"
     
    def __str__(self):
       return f"{self.user.username} User Pin"

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'UserPins'
        verbose_name_plural = 'UserPins'
        
class VerificationCode(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE,related_name='verificationcode')
    code = models.CharField(_("code"), max_length=255 ,blank=True)
    updated = models.DateTimeField(auto_now=True,)
    
    # this handles payment pin 
    def setCode(self,row_code):  
        self.code = make_password(str(row_code))
        self.save()
        
    def checkCode(self,row_code):
        return check_password(str(row_code),self.code)
    
    def show_code(self):
        return f"{self.code[:6]}****{self.code[-6:]}"


    def __str__(self):
       return f"{self.show_code} User Code"

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'UserCode'
        verbose_name_plural = 'UserCode' 