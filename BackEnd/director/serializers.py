from rest_framework import serializers

from director.models import Director
from core .serializers import DirectorSchoolSerializer
from authUser.serializers import MiniUserSerializer
import  json
from django.db import transaction
class DirectorDetailSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()
    user = MiniUserSerializer(read_only=True)
    directorschools = DirectorSchoolSerializer(many=True, read_only=True)
    class Meta:  
        model = Director 
        fields ='__all__'
        read_only_fields = ['id', 'joined_at']
        
    def get_picture(self, obj):
        return obj.picture.url if obj.picture else None
    
    def update(self, instance, validated_data):
        # print('validated_data: ', validated_data)
        request = self.context['request']
        # for d in request.data.copy() :
        #     print(d)
        picture_file = request.FILES.get("picture")
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            if picture_file:
                instance.picture = picture_file
            instance.save()
        return instance
