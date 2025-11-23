import random
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError ,AuthenticationFailed

from.models import User, KYC


def generate_5_otp() :
    code = random.randint(12345,98769)
    return  code 

class MiniUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
           "id","username","phone_number","email","picture",'first_name','last_name','middle_name'
            "refarrel_code","kyc_submitted",
            "kyc_confirmed","email_varified","is_staff","is_superuser",
        ]
        extra_kwargs = {'id' : {"read_only" : True},"password":{"write_only":True}}
class MiniKYCSerializer(ModelSerializer):
    class Meta:
        model = KYC
        fields = "__all__"
        extra_kwargs  ={'id' : {"read_only" : True}}    
                            
class UserSerializer(ModelSerializer):
    kyc = MiniKYCSerializer(KYC)
    # account =  AccountSerializer(Account)
    class Meta:
       model = User
       exclude = ['password',]
       extra_kwargs  ={'id' : {"read_only" : True},"password":{"write_only":True}}
        
class KYCSerializer(ModelSerializer):
    user = MiniUserSerializer(User,many = True)
    class Meta:
        model = KYC
        fields = "__all__"
        extra_kwargs  ={'id' : {"read_only" : True}}

# custom serializer configuard in settings to hadle login tokens 
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer) :
    userOtp = None 
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.otp =  kwargs['data'].get('otp',None)
        CustomTokenObtainPairSerializer.userOtp = self.otp
        
    # Add custom claims
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        user_data = UserSerializer(user).data
        if user.log_with_otp :
            if  user.verificationcode.checkCode(cls.userOtp) :
                # user.save()
                # we will send confirm login email 
                # send message here
                return token,user_data
            else :
                raise AuthenticationFailed('invalid otp')
        else :
            if not user.is_active : # account inactive
                raise AuthenticationFailed('user account is inactive contact support!')
            return{token,user}