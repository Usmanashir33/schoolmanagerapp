from rest_framework import serializers

from subject .models import Subject
    
class SubjectSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = Subject 
        fields ='__all__'
        read_only_fields = ['id', 'added_at']
    