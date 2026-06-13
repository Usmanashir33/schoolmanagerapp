import json
from os import name
from rest_framework import serializers
from django.db import transaction

from school.models import FinanceSettings, School, SchoolBankAccount,Term,Session,Templates
from school.models import ActivityLog, SchoolPermission, SchoolRole

class TemplatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Templates
        read_only_fields = ['id']
        fields = '__all__'  
        
from rest_framework import serializers
from django.db import transaction

class SchoolSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField(read_only =True)
    class Meta:  
        model = School
        fields ='__all__'
        read_only_fields = ['id', 'joined_at','ref_id','director']
    
    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None
    
    def update(self, instance, validated_data):
        request = self.context['request']
        logo = request.FILES.get("logo")
        

        # update only provided fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if logo :
            instance.logo = logo

        # save updated instance
        instance.save()

        return instance

class SchoolBankAccountSerializer(serializers.ModelSerializer):
    finance = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SchoolBankAccount
        fields = '__all__'
        read_only_fields = ['id', 'finance']

    def create(self, validated_data):
        finance = self.context.get("finance")
        with transaction.atomic():
            is_default = validated_data.get("is_default", False)
            if is_default:
                finance.bank_accounts.filter(is_default=True).update(is_default=False)
            return SchoolBankAccount.objects.create(
                finance=finance,
                **validated_data
            )
            
    def update(self, instance, validated_data):
        with transaction.atomic():
            is_default = validated_data.get("is_default", False)
            if is_default:
                instance.finance.bank_accounts.filter(is_default=True).exclude(id=instance.id).update(is_default=False)
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance
class FinanceSettingsSerializer(serializers.ModelSerializer):
    bank_accounts = SchoolBankAccountSerializer(many=True, read_only=True)
    class Meta:
        model = FinanceSettings
        read_only_fields = ['id']
        fields = '__all__'  
    
class TermSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = Term  
        fields = "__all__"
        read_only_fields = ['id',]
class SessionSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = Session 
        fields = "__all__"
        read_only_fields = ['id',] 
class SchoolPermissionSerializer(serializers.ModelSerializer) :
    class Meta:
        model = SchoolPermission
        fields = ['id','school','name','description']
        read_only_fields = ['id','name']
        
    def create(self, validated_data) :
        created = super().create(validated_data)
        return created
    
    def update(self, instance, validated_data) :
        for attr, value in validated_data.items() :
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class SchoolRoleSerializer(serializers.ModelSerializer) :
    permissions = SchoolPermissionSerializer(many=True, read_only=True)
    permissionIds = serializers.SerializerMethodField(read_only=True)
    users = serializers.SerializerMethodField(read_only=True)
    get_permissionIds = lambda self, obj: [perm.id for perm in obj.permissions.all()]
    def get_users(self, obj):

        users_data = []
        if not  hasattr(obj, "users") :
            return users_data
        
        users = obj.users.all()
        for user in users:

            user_data = {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "picture": user.picture.url if user.picture else None,
                "email": user.email,
            }
            users_data.append(user_data)

        return users_data
        
    class Meta:
        model = SchoolRole
        fields = '__all__'
        read_only_fields = ['id']
        
    def create(self, validated_data):
        perms = self.context['perms']
        created= super().create(validated_data)
        
        if created and perms :
            created.permissions.set(perms)
        return created 
    
    def update(self, instance, validated_data):
        perms = self.context['perms']
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if perms :
            instance.permissions.set(perms)
        return instance
class SchoolSettingsSerializer(serializers.ModelSerializer) :
    class Meta:  
        model = School 
        fields ='__all__'
        read_only_fields = ['id', 'ref_id', 'joined_at']
    
    def update(self, instance, validated_data):
        request = self.context['request']
        # school_sesions_names = request.data.getlist("availableSessions")
        # school_terms_names = request.data.getlist("availableTerms")
        
        current_term_name = request.data.get("term")
        current_session_name = request.data.get("session")
        
        autoPromotion = request.data.get("autoPromotion")
        lockPastRecords = request.data.get("lockPastRecords")
        gradingSystem  = request.data.get("gradingSystem")
        
        # picture_file = request.FILES.get("picture")

        
        if request.method == 'PUT' or request.method == 'PATCH':
            # for attr, value in validated_data.items():
            #     setattr(instance, attr, value)
            
            # if len(school_sesions_names) :
            #     for sesion_name in school_sesions_names:
            #         session, created = Session.objects.get_or_create(
            #             name=sesion_name,
            #             school=instance
            #         )
            #         if created:
            #             instance.sessions.add(session)
                        
            # if len(school_terms_names) :
            #     for term_name in school_terms_names :
            #         term,created = Term.objects.get_or_create(
            #             name = term_name,
            #             school = instance
            #         )
            #         if created :
            #             instance.terms.add(term)
                        
            if instance.terms.filter(name = current_term_name).exists() :
                instance.terms.filter(is_current=True).update(is_current=False)
                current_term = instance.terms.filter(name = current_term_name).first()
                current_term.is_current = True
                current_term.save()
                
            if instance.sessions.filter(name = current_session_name).exists() :
                instance.sessions.filter(is_current=True).update(is_current=False)
                current_session = instance.sessions.filter(name = current_session_name).first()
                current_session.is_current = True
                current_session.save()
                
            update_prom = False if autoPromotion == 'false' else True if autoPromotion == 'true' else None
            if update_prom is not None:
                instance.auto_promotion = update_prom
                instance.save()
                
            update_lock = False if lockPastRecords == 'false' else True if lockPastRecords == 'true' else None
            if  update_lock is not None:
                instance.lock_records = update_lock
                instance.save()
                
            update_grading = False if gradingSystem == 'false' else True if gradingSystem == 'true' else None  
            if update_grading is not None:
                instance.grading_system = update_grading
                instance.save()
                
            instance.save()

        return instance

class ActivityLogSerializer(serializers.ModelSerializer):
    userName = serializers.SerializerMethodField()
    class Meta:
        model = ActivityLog

        fields = [
            "id",
            "action",
            "module",
            "description",
            "created_at",
            "user",
            "userName",
            "school",
        ]

    def get_userName(self, obj):
        user = obj.user

        if hasattr(user, "username") and user.username:
            return f"{user.role}-({user.username})"

        return getattr(
            user,
            "username",
            "Unknown User"
        )