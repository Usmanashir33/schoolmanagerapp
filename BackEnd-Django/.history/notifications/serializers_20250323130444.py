from rest_framework.serializers import ModelSerializer
from .
class MoneyTransactionSerializer(ModelSerializer):
    class Meta:
        model =MoneyTransaction
        fields = "__all__"
        extra_kwargs  ={'id' : {"read_only" : True}}
        
