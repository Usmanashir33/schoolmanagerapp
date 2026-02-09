from rest_framework import serializers
from .models import SchoolSection


class SchoolSectionSerializer(serializers.ModelSerializer):
    # school = SchoolSerializer(read_only=True)
    class Meta:  
        model = SchoolSection 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
        
class SchoolSectionDetailSerializer(serializers.ModelSerializer):
    class Meta:  
        model = SchoolSection 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
