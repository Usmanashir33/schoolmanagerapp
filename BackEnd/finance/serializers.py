
from rest_framework import serializers
from academics.serializers import ClassRoomDetailSerializer
from staff.models import Staff , ActivityRole
from core.serializers import BankSerializer 
from authUser.serializers import MiniUserSerializer
import json 
from django.db import transaction
from .models import ClassFeeSetting, PaymentInitiation,StudentTransaction
from academics.models import ClassRoom
from student .models import StudentClassEnrollment ,Student
from student.serializers import MiniStudentSerializer

class SchoolFeeSerializer(serializers.ModelSerializer):
    classIds = serializers.SerializerMethodField(read_only=True, source='class_rooms')
    createdAt = serializers.DateTimeField(format="%a %m/%d/%Y, %I:%M:%S %p", read_only=True, source='created_at')
    updatedAt = serializers.DateTimeField(format="%a %m/%d/%Y, %I:%M:%S %p", read_only=True, source='updated_at')

    class Meta:
        model = ClassFeeSetting
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_classIds(self, obj):
        classes = ClassRoomDetailSerializer(obj.class_rooms.all(), many=True).data
        return classes if classes else []
    
    def create(self, validated_data):
        request = self.context["request"]
        class_rooms = request.data.get("classIds", [])

        with transaction.atomic():
            school = validated_data.get("school")
            name = validated_data.get("name")

            classes = ClassRoom.objects.filter(
                id__in=class_rooms,
                section__school=school
            )

            # validation for school existing clases
            if not classes.exists():
                raise serializers.ValidationError({
                    "classIds": "No valid classes found for this school."
                })

            #  Check duplicates (AFTER classes exist)
            existing = ClassFeeSetting.objects.filter(
                class_rooms__in=classes,
                school=school,
                # name=name
            ).values_list("class_rooms__id", flat=True).distinct()

            if existing:
                raise serializers.ValidationError({
                    "classIds": f"Fee already exists for class IDs: {list(existing)}"
                })

            # ✅ Create
            class_fee_setting = ClassFeeSetting.objects.create(**validated_data)
            class_fee_setting.class_rooms.set(classes)
            return class_fee_setting
    
    def update(self, instance, validated_data):
        request = self.context["request"]
        class_ids = request.data.get("classIds", None)

        with transaction.atomic():
            school = validated_data.get("school", instance.school)
            name = validated_data.get("name", instance.name)

            # ✅ Update basic fields first
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # ✅ If classIds is provided → update relations
            if class_ids is not None:
                classes = ClassRoom.objects.filter(
                    id__in=class_ids,
                    section__school=school
                )

                if not classes.exists():
                    raise serializers.ValidationError({
                        "classIds": "No valid classes found for this school."
                    })

                # ✅ EXCLUDE current instance (KEY DIFFERENCE FROM CREATE)
                existing = ClassFeeSetting.objects.filter(
                    class_rooms__in=classes,
                    school=school,
                    # name = name 
                ).exclude(id=instance.id) 
                if existing:
                    raise serializers.ValidationError({
                        "classIds": f"Some classes already have fee settings: {list(existing)}"
                    })
                # ✅ Replace relationships (handles add/remove automatically)
                instance.class_rooms.set(classes)

            return instance
        
class PaymentInitiationReadSerializer(serializers.ModelSerializer):
    students = MiniStudentSerializer(read_only = True,many=True)
    termName = serializers.CharField(source='term.name',read_only = True)
    sessionName = serializers.CharField(source='session.name',read_only = True)
    
    class Meta:
        model = PaymentInitiation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at','students','ref_number']
        
class PaymentInitiationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentInitiation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at','students','ref_number']

    
    def create(self, validated_data):
        school = validated_data.get("school")
        request = self.context["request"]
        student_ids = request.data.get("students", [])
        if isinstance(student_ids, str):
            student_ids = json.loads(student_ids)
            
        students = Student.objects.filter(
            id__in=student_ids,
            school=school
        )
        with transaction.atomic():
            # print('students: ', students)
            # validation for school existing clases
            if not students.exists():
                raise serializers.ValidationError({
                    "students": "No valid students found for this school."
                })
            
            #  Create
            payment = PaymentInitiation.objects.create(**validated_data)
            payment.students.set(students)
            return payment
    
    # def update(self, instance, validated_data):
    #     request = self.context["request"]
    #     class_ids = request.data.get("classIds", None)

    #     with transaction.atomic():
    #         school = validated_data.get("school", instance.school)
    #         name = validated_data.get("name", instance.name)

    #         # ✅ Update basic fields first
    #         for attr, value in validated_data.items():
    #             setattr(instance, attr, value)
    #         instance.save()

    #         # ✅ If classIds is provided → update relations
    #         if class_ids is not None:
    #             classes = ClassRoom.objects.filter(
    #                 id__in=class_ids,
    #                 section__school=school
    #             )

    #             if not classes.exists():
    #                 raise serializers.ValidationError({
    #                     "classIds": "No valid classes found for this school."
    #                 })

    #             # ✅ EXCLUDE current instance (KEY DIFFERENCE FROM CREATE)
    #             existing = ClassFeeSetting.objects.filter(
    #                 class_rooms__in=classes,
    #                 school=school,
    #                 # name = name 
    #             ).exclude(id=instance.id) 
    #             if existing:
    #                 raise serializers.ValidationError({
    #                     "classIds": f"Some classes already have fee settings: {list(existing)}"
    #                 })
    #             # ✅ Replace relationships (handles add/remove automatically)
    #             instance.class_rooms.set(classes)

    #         return instance
        
class ClassConfiguredSerializer(serializers.ModelSerializer) :
    configInfo = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = ClassRoom
        fields = '__all__'
        read_only_fields = ['id', 'joined_at',]
        
    def get_configInfo(self,obj) : # get total students in the class 
        term = self.context.get('term')
        session = self.context.get('session')
        
        class_students = Student.objects.filter (
            class_rooms__class_room = obj ,
            class_rooms__status__in  = ["active",'enrolled'],
        ) 
        
        configured_student = class_students.filter(
            student_fees__transaction_type = 'FEE',
            student_fees__session = session ,
            student_fees__term = term ,
        )
        configuredAmount = configured_student.values_list("student_fees__total_amount").distinct().first()
        
        un_configured_student = class_students.count() - configured_student.count()
        in_active_students = class_students.filter(user__is_active = False).count()
        result = {
            "totalStudents" : class_students.count() ,
            "configuredAmount": configuredAmount ,
            'configuredStudents' : configured_student.count(),
            'UnconfiguredStudents' :un_configured_student,
            "inActiveStudents" : in_active_students 
        }
        return result 
    
class StudentLedgerSerializer(serializers.ModelSerializer) :
    # student = MiniStudentSerializer(read_only = True)
    payment_details =  serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = StudentTransaction
        fields = '__all__'
        read_only_fields = ['id', 'created_at','due_date']
    def get_payment_details(self, obj):
        payment_source = getattr(obj, "payment_source", None)
        
        if not payment_source:
            return None
       
        return {
            "id": payment_source.id,
            "ref_number": payment_source.ref_number,
            "payer": payment_source.payer,
            "payment_method": payment_source.payment_method,
            "total_amount": payment_source.total_amount,
        }
        
    
class DirectorFinanceDashbordSerializer(serializers.ModelSerializer) :
    payment_details = serializers.SerializerMethodField(read_only = True)
    name = serializers.SerializerMethodField(read_only = True)
    admission_number = serializers.SerializerMethodField(read_only = True)
    active_classes = serializers.SerializerMethodField(read_only = True)
    
    
    class Meta:
        model = StudentTransaction
        fields = '__all__'
        read_only_fields = ['id', 'created_at','due_date',]
        
    def get_name(self,obj):
        first_name = obj.student.first_name
        last_name = obj.student.last_name
        return first_name + " " + last_name
    
    def get_payment_details(self, obj):
        payment_source = getattr(obj, "payment_source", None)
        
        if not payment_source:
            return None
       
        return {
            "id": payment_source.id,
            "ref_number": payment_source.ref_number,
            "payer": payment_source.payer,
            "payment_method": payment_source.payment_method,
            "total_amount": payment_source.total_amount,
        }
   
    def get_admission_number(self,obj):
        admission_number = obj.student.admission_number
        return admission_number
        
    def get_active_classes(self,obj):
        active_classes = StudentClassEnrollment.objects.filter( 
            student = obj.student,
            status__in = ["active","enrolled",]
        ).values_list("class_room",flat=True)
        
        return active_classes
        
   