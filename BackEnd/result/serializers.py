from rest_framework import serializers

from  academics.models import ClassRoom,Subject
from   school.models import School, Session, Term
from  student.models import Student, Student, StudentClassEnrollment
from  .models import ResultBatch, StudentResult,ReportSheet,StudentCharacterSkill,CharacterBatch,ApprovalRecord
from teacher.models import Teacher
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q

from academics.serializers import ClassRoomDetailSerializer
from student.serializers import StudentSerializer
from school.serializers import SessionSerializer,TermSerializer


class StudentCharacterSkillSerializer(serializers.ModelSerializer):
    studentId = serializers.PrimaryKeyRelatedField(source='student.id', read_only=True)
    class Meta:
        model = StudentCharacterSkill
        fields = "__all__"
        
class SkillBatchReadSerializer(serializers.ModelSerializer):
    charAndSkills = StudentCharacterSkillSerializer(many=True)
    isUploaded = serializers.BooleanField(source='is_uploaded', read_only=True)
    isLocked  = serializers.BooleanField(source='is_locked', read_only=True)
    isUpdated = serializers.BooleanField(source='last_updated', read_only=True)
    lastUpdated = serializers.DateTimeField(source='last_updated', read_only=True)

    classId   = serializers.PrimaryKeyRelatedField(source='class_room', read_only=True)
    
    class Meta:
        model = CharacterBatch
        fields = "__all__"
        
class StudentCharacterWriteSkillSerializer(serializers.Serializer):
    studentId = serializers.UUIDField()
    punctuality = serializers.FloatField(required=False, default=3)
    honesty = serializers.FloatField(required=False, default=3)
    neatness = serializers.FloatField(required=False, default=3)
    leadership = serializers.FloatField(required=False, default=3)
    handwriting = serializers.FloatField(required=False, default=3)
    verbal_fluency = serializers.FloatField(required=False, default=3)
    creativity = serializers.FloatField(required=False, default=3)

    def validate(self, data):
        if data["punctuality"] > 5:
            raise serializers.ValidationError("trait cannot exceed 5")
        if data["honesty"] > 5:
            raise serializers.ValidationError("trait cannot exceed 5")
        if data["neatness"] > 5:
            raise serializers.ValidationError("trait cannot exceed 5")
        if data["leadership"] > 5:
            raise serializers.ValidationError("trait cannot exceed 5")
        if data["handwriting"] > 5:
            raise serializers.ValidationError("trait cannot exceed 5")
        if data["verbal_fluency"] > 5:
            raise serializers.ValidationError("trait cannot exceed 5")
        if data["creativity"] > 5:
            raise serializers.ValidationError("trait cannot exceed 5")
        return data
    
class StudentResultWriteSerializer(serializers.Serializer):
    studentId = serializers.UUIDField()
    ca1 = serializers.FloatField(required=False, default=0)
    ca2 = serializers.FloatField(required=False, default=0)
    exam = serializers.FloatField(required=False, default=0)

    def validate(self, data):
        if data["ca1"] > 20:
            raise serializers.ValidationError("CA1 cannot exceed 20")
        if data["ca2"] > 20:
            raise serializers.ValidationError("CA2 cannot exceed 20")
        if data["exam"] > 60:
            raise serializers.ValidationError("Exam cannot exceed 60")
        return data

class ResultBatchUpsertSerializer(serializers.Serializer):
    school = serializers.UUIDField()
    class_room = serializers.UUIDField()
    subject = serializers.UUIDField()
    session = serializers.UUIDField()
    term = serializers.UUIDField()
    teacher = serializers.UUIDField()
    
    scores = StudentResultWriteSerializer(many=True)
    
    isUploaded = serializers.BooleanField(default=False)

    @transaction.atomic
    def create(self, validated_data):
        results_data = validated_data.pop("scores")

        # 🔒 Validate all data is valid Exists
        school = School.objects.filter(
            id = validated_data["school"],
            terms__id=validated_data["term"],
            sessions__id=validated_data["session"],
            teachers__id=validated_data["teacher"],
        ).first()
        
        if not school:
            raise serializers.ValidationError(f"School with this details does not exist.")
        
        teacher_id = validated_data.get("teacher")
        teacher = school.teachers.filter(id=teacher_id).first() if teacher_id else None
        
        # validate subject also
        subject = school.subjects.filter(id=validated_data["subject"]).first()
        if not subject:
            raise serializers.ValidationError(f"Subject with id {validated_data['subject']} does not exist.")
        
        # validate class also 
        class_room = ClassRoom.objects.filter(section__school = school.id , id=validated_data["class_room"]).first()
        if not class_room:
            raise serializers.ValidationError(f"ClassRoom with id {validated_data['class_room']} does not exist.")
        
        # validate session also         
        session = Session.objects.filter(id=validated_data["session"]).first()  
        if not session:
            raise serializers.ValidationError(f"Session with id {validated_data['session']} does not exist.")   
        
        # validate term also
        term = Term.objects.filter(id=validated_data["term"]).first()
        if not term:
            raise serializers.ValidationError(f"Term with id {validated_data['term']} does not exist.")
        
        # 🔒 Get or Create Batch
        batch, created = ResultBatch.objects.get_or_create( 
            class_room=class_room,
            subject=subject ,
            session=session ,
            term=term ,
            defaults = {"teacher": teacher}
        )
        batch.is_uploaded = True 
        batch.approved = False 
        batch.save()
        
        # validate if batch is not locked before allowing updates
        if batch.is_locked:
            raise serializers.ValidationError("This result batch is locked and cannot be modified.")
        
        # 🔒 Validate Students Belong to Class
        class_students = set(
            StudentClassEnrollment.objects.filter(
                class_room=batch.class_room,
                status__in=['active', 'enrolled'],
            ).values_list('student__id', flat=True)
        )
        
        existing_results = {
            result.student.id : result
            for result in batch.scores.all()
        }
        
        for result_data in results_data:
            student_id = str(result_data["studentId"])

            # 🚨 Prevent fake student injection
            if student_id not in class_students:
                continue # pass silently
            total = ( 
                float(result_data.get("ca1", 0)) +
                float(result_data.get("ca2", 0)) + 
                float(result_data.get("exam", 0))
            )

            # ✅ If result exists → update 
            if student_id in existing_results:
                obj = existing_results[student_id]
                obj.ca1 = float(result_data.get("ca1", obj.ca1))  
                obj.ca2 = float(result_data.get("ca2", obj.ca2))  
                obj.exam = float(result_data.get("exam", obj.exam))  
                obj.total = total
                obj.save()

            # ✅ If not exists → create
            else:
                student = school.students.filter(id=student_id).first()
                if not student:
                    raise serializers.ValidationError(f"Student with id {student_id} does not exist.")
                StudentResult.objects.create(
                    batch=batch,
                    student=student,
                    ca1= float(result_data.get("ca1", 0)),
                    ca2=float(result_data.get("ca2", 0)),
                    exam=float(result_data.get("exam", 0)),
                    total=total
                )

        # 🔄 Update Batch Status
        total_students = len(class_students)
        filled_results = batch.scores.filter(total__gt=0).count()

        if filled_results == 0:
            batch.status = "EMPTY"
            
        elif filled_results < total_students:
            batch.status = "PARTIAL"
        else:
            batch.status = "COMPLETE"
        batch.save()
        return batch

class StudentCharAndSkillsUpsertSerializer(serializers.Serializer):
    school = serializers.UUIDField()
    class_room = serializers.UUIDField()
    session = serializers.UUIDField()
    term = serializers.UUIDField()
    
    charAndSkills = StudentCharacterWriteSkillSerializer(many = True)
    isUploaded = serializers.BooleanField(default=False)
    
    
    @transaction.atomic
    def create(self, validated_data):
        charAndSkills = validated_data.pop("charAndSkills")
        # 🔒 Validate all data is valid Exists
        school = School.objects.filter(
            id = validated_data["school"],
            terms__id=validated_data["term"],
            sessions__id=validated_data["session"],
        ).first()
        
        if not school:
            raise serializers.ValidationError(f"School with this details does not exist.")
        
        teacher_id = validated_data.get("teacher")
        teacher = school.teachers.filter(id=teacher_id).first() if teacher_id else None
        
        # validate class also 
        class_room = ClassRoom.objects.filter(section__school = school.id , id=validated_data["class_room"]).first()
        if not class_room:
            raise serializers.ValidationError(f"ClassRoom with id {validated_data['class_room']} does not exist.")
        # validate term also
        term = Term.objects.filter(id=validated_data["term"]).first()
        if not term:
            raise serializers.ValidationError(f"Term with id {validated_data['term']} does not exist.")
        session = Session.objects.filter(id=validated_data["session"]).first()
        if not session:
            raise serializers.ValidationError(f"Session with id {validated_data['session']} does not exist.")
        
        # 🔒 Validate Students Belong to Class
        class_students = school.students.filter(
                class_rooms__class_room = class_room,
                class_rooms__status__in=['active', 'enrolled'] ,
            )
        
        # 🔒 Get or Create Batch
        batch, created = CharacterBatch.objects.get_or_create( 
            class_room=class_room,
            session=session ,
            term=term ,
            school=school
        )
        batch.is_uploaded = True 
        batch.approved = False 
        
        batch.save()
        
        # validate if batch is not locked before allowing updates
        if batch.is_locked:
            raise serializers.ValidationError("This skill batch is locked and cannot be modified.")
        
        existing_skills = {
            skill.student.id : skill
            for skill in batch.charAndSkills.all()
        }
        chars = []
        for result_data in charAndSkills:
            student_id = result_data["studentId"]
            student = class_students.filter(id=student_id).first()

            if not student:
                continue  # skip fake injection safely

            obj, _ = StudentCharacterSkill.objects.update_or_create(
                batch = batch,
                student=student,
                defaults={
                    "punctuality": result_data.get('punctuality'),
                    "honesty": result_data.get('honesty'),
                    "neatness": result_data.get("neatness"),
                    "leadership": result_data.get("leadership"),
                    "handwriting": result_data.get("handwriting"),
                    "verbal_fluency": result_data.get("verbal_fluency"),
                    "creativity": result_data.get("creativity")
                }
            )
            chars.append(obj)
        # get batch status 
        students_count = class_students.count()
        students_with_record = class_students.filter(skills__in = chars).count()
        if students_with_record == students_count :
            batch.status = "COMPLETE"
        elif students_with_record < 1 :
            batch.status = "EMPTY"
        else :
            batch.status = "PARTIAL"
        batch.save()
        return batch 
    
class StudentResultReadSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    studentId = serializers.PrimaryKeyRelatedField(source='student', read_only=True)
    subject_name = serializers.PrimaryKeyRelatedField(source='batch.subject.name', read_only=True)
    subject_code = serializers.PrimaryKeyRelatedField(source='batch.subject.code', read_only=True)
    subject_credits = serializers.PrimaryKeyRelatedField(source='batch.subject.credits', read_only=True)

    class Meta:
        model = StudentResult
        fields = ["id","studentId","student_name","subject_name","subject_code","subject_credits","ca1", "ca2", "exam", "total",'grade','remark']

class ResultBatchReadSerializer(serializers.ModelSerializer):
    scores    = StudentResultReadSerializer(many=True)
    teacherId = serializers.PrimaryKeyRelatedField(source='teacher', read_only=True)
    subjectId = serializers.PrimaryKeyRelatedField(source='subject', read_only=True)
    classId   = serializers.PrimaryKeyRelatedField(source='class_room', read_only=True)
    isUploaded = serializers.BooleanField(source='is_uploaded', read_only=True)
    isLocked  = serializers.BooleanField(source='is_locked', read_only=True)
    isUpdated = serializers.BooleanField(source='last_updated', read_only=True)
    lastUpdated = serializers.DateTimeField(source='last_updated', read_only=True)

    class Meta:
        model = ResultBatch
        fields = "__all__"



class ReportSheetFetchSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only = True)
    class_room = ClassRoomDetailSerializer(read_only = True)
    term =  TermSerializer(read_only = True)
    session =  SessionSerializer(read_only = True)
    scores = serializers.SerializerMethodField(read_only=True)
    classTotalStudents = serializers.IntegerField(source="total_class_students",read_only =True)
    skills = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ReportSheet
        fields = "__all__"
    
    def get_scores(self,obj):
        scores =  self.context['scores'] 
        return StudentResultReadSerializer(scores,many=True).data
    
    def get_skills(self,obj):
        skill = obj.student.skills.filter(
            batch__approved = True ,
            batch__term = obj.term,
            batch__session = obj.session,
            batch__class_room = obj.class_room
        ).first()
        
        if not skill :
            return None
        return StudentCharacterSkillSerializer(skill).data
    
    
class ApprovalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRecord
        fields = "__all__"
    
   
