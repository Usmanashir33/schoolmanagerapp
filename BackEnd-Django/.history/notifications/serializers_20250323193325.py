from rest_framework.serializers import ModelSerializer
from .models import Notification


class NotificationSerializer(ModelSerializer):
    class Meta:
        model =Notification
        fields = "__all__"
        extra_kwargs  ={'id' : {"read_only" : True}}
        
