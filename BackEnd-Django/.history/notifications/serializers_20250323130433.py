from rest_framework.serializers import Mo
class MoneyTransactionSerializer(ModelSerializer):
    class Meta:
        model =MoneyTransaction
        fields = "__all__"
        extra_kwargs  ={'id' : {"read_only" : True}}
        
