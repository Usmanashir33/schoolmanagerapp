 
from rest_framework import serializers
from staff.models import Staff
from authUser.serializers import MiniUserSerializer

class StaffSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    class Meta:
        model = Staff
        fields = '__all__'
class MiniStaffSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(read_only=True)
    class Meta:
        model = Staff
        fields = '__all__'
       
        