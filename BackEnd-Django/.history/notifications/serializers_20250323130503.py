from rest_framework.serializers import ModelSerializer
from .models import MoneyNotification
class MoneyTransactionSerializer(ModelSerializer):
    class Meta:
        model =MoneyNotification
        fields = "__all__"
        extra_kwargs  ={'id' : {"read_only" : True}}
        
