from rest_framework import serializers

from subject .models import Subject
from classroom.models import ClassRoom
from django.db import transaction

    
class SubjectSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = Subject   
        fields ='__all__' 
        read_only_fields = ['id', 'added_at']
    
class SubjectDetailSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = Subject 
        fields ='__all__' 
        read_only_fields = ['id', 'added_at']
        
    def create(self, validated_data) :
        request = self.context["request"]
        class_rooms = request.data.get("class_rooms", [])
        with transaction.atomic():
            subject = Subject.objects.create(**validated_data)
            
            if class_rooms:
                subject.class_room.set(ClassRoom.objects.filter(id__in = class_rooms))
            subject.save()
                
        return subject 
    
    # def update(self, instance, validated_data):
    #     request = self.context["request"]
    #     bank_details_data = request.data.get("bank_details", [])
    #     class_room_ids = request.data.getlist("class_rooms", [])
    #     picture_file = request.FILES.get("picture")
        
    #      # ✅ FIX: safe JSON parsing
    #     if bank_details_data:
    #         try:
    #             bank_data = json.loads(bank_details_data)
    #         except (TypeError, ValueError):
    #             bank_data = None
        
    #     with transaction.atomic():
    #         # update teacher 
    #         for field ,value in validated_data.items() :
    #             setattr(instance,field,value)
                
    #         bank = instance.bank_details
    #         if not bank : #create 
    #             # print('bank: ', bank)
    #             bank = BankSerializer(data =bank_data)
    #         else : # Update 
    #             bank = BankSerializer(bank , data =bank_data,partial=True )
            
    #         if bank.is_valid() :
    #             bank.save()
    #             instance.bank_details = bank.instance
    #         if class_room_ids:
    #             instance.class_room.set(
    #                 ClassRoom.objects.filter(id__in=class_room_ids)
    #             )
                
    #         if picture_file:
    #             instance.picture = picture_file
    #         instance.save()
                
    #     return instance 
