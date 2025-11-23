import random
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError ,AuthenticationFailed

from.models import Account,AccountNumber,MoneyTransaction,WithdrawalAccount
from authUser.models import User ,KYC

def generate_verifed_email_otp() :
    code = random.randint(12345,98769)
    # code_exit = User.objects.get(email_verification_code = code).exists()
    return  code 
    # return  code if not code_exit else  generate_verifed_email_otp()

class MiniUserSerializer(ModelSerializer):
    class Meta:
       model = User
       exclude = ['password',"lock_password","payment_pin",'email_verification_code']
       extra_kwargs  ={'id' : {"read_only" : True},"password":{"write_only":True}}
    
        
class KYCSerializer(ModelSerializer):
    # user = MiniUserSerializer(User,many = True)
    class Meta:
        model = KYC
        fields = "__all__"
        extra_kwargs  ={'id' : {"read_only" : True}}
        
class AccountNumberSerializer(ModelSerializer):
    class Meta:
        model =AccountNumber
        exclude = ['flw_ref',]
        extra_kwargs  ={'id' : {"read_only" : True}}
        
class WithdrawalAccountSerializer(ModelSerializer): 
    class Meta:
        model =WithdrawalAccount
        fields = "__all__"
        extra_kwargs  ={'id' : {"read_only" : True}}
        
class AccountSerializer(ModelSerializer):
    accountnumbers  = AccountNumberSerializer(AccountNumber,many = True)
    class Meta:
        model =Account
        fields = "__all__"
        extra_kwargs  ={'id' : {"read_only" : True}}
        
class MoneyTransactionSerializer(ModelSerializer):
    user = MiniUserSerializer(User)
    receiver = MiniUserSerializer(User)
    sender = MiniUserSerializer(User)
    class Meta:
        model =MoneyTransaction
        fields = "__all__"
        extra_kwargs  ={'id' : {"read_only" : True}}
        
