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
from student.serializers import StudentSerializer,MiniStudentSerializer
from school.serializers import SessionSerializer,TermSerializer,TemplatesSerializer,MiniSchoolSerializer


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

    is_submitted = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        fields = [
            "punctuality",
            "honesty",
            "neatness",
            "leadership",
            "handwriting",
            "verbal_fluency",
            "creativity",
        ]

        for field in fields:
            value = data.get(field, 3)

            # Prevent negative values
            if value < 0:
                value = 0

            # Cap maximum at 5
            if value > 5:
                value = 5

            data[field] = value

        return data
    

class StudentResultWriteSerializer(serializers.Serializer):
    studentId = serializers.UUIDField()

    ca1 = serializers.FloatField(required=False, default=0)
    ca2 = serializers.FloatField(required=False, default=0)
    exam = serializers.FloatField(required=False, default=0)

    ca1Abs = serializers.BooleanField(required=False, default=False)
    ca2Abs = serializers.BooleanField(required=False, default=False)
    examAbs = serializers.BooleanField(required=False, default=False)
    is_submitted = serializers.BooleanField(required=False, default=False)

    def validate(self, data):

        school = self.context.get("school")

        max_marks = (
            school.max_marks
            if school and school.max_marks
            else {
                "ca1": 20,
                "ca2": 20,
                "exam": 60,
            }
        )

        if data.get("ca1", 0) > max_marks.get("ca1", 20):
            raise serializers.ValidationError(
                f"CA1 cannot exceed {max_marks['ca1']}"
            )

        if data.get("ca2", 0) > max_marks.get("ca2", 20):
            raise serializers.ValidationError(
                f"CA2 cannot exceed {max_marks['ca2']}"
            )

        if data.get("exam", 0) > max_marks.get("exam", 60):
            raise serializers.ValidationError(
                f"Exam cannot exceed {max_marks['exam']}"
            )

        return data
class ResultBatchUpsertSerializer(serializers.Serializer):
    school = serializers.UUIDField()
    class_room = serializers.UUIDField()
    subject = serializers.UUIDField()
    session = serializers.UUIDField()
    term = serializers.UUIDField()
    teacher = serializers.UUIDField()
    isUploaded = serializers.BooleanField(default=False)
    
    scores = StudentResultWriteSerializer(many=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["scores"].child.context.update(
            self.context
        )

    @transaction.atomic
    def create(self, validated_data):
        results_data = validated_data.pop("scores")

        # 🔒 Validate all data is valid Exists
        school = School.objects.filter(
            id = validated_data["school"],
            terms__id=validated_data["term"],
            sessions__id=validated_data["session"],
            teachers__id=validated_data["teacher"],
        ).prefetch_related("teachers",'subjects','classrooms','sessions','terms').first()
        
        if not school:
            raise serializers.ValidationError(f"School with this details does not exist.")
        
        teacher_id = validated_data.get("teacher")
        teacher = school.teachers.filter(id=teacher_id).first() if teacher_id else None
        
        # validate subject also
        subject = school.subjects.filter(id=validated_data["subject"]).first()
        if not subject:
            raise serializers.ValidationError(f"Subject with id {validated_data['subject']} does not exist.")
        
        # validate class also 
        class_room = school.classrooms.filter(id=validated_data["class_room"]).first()
        if not class_room:
            raise serializers.ValidationError(f"ClassRoom with id {validated_data['class_room']} does not exist.")
        
        # validate session also         
        session = school.sessions.filter(id=validated_data["session"]).first()  
        if not session:
            raise serializers.ValidationError(f"Session with id {validated_data['session']} does not exist.")   
        
        # validate term also
        term = school.terms.filter(id=validated_data["term"]).first()
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
        # validate if batch is not locked before allowing updates
        if batch.is_locked or batch.on_submit or batch.approved:
            raise serializers.ValidationError("This batch cannot be modified.")
        
        
        batch.save()
        
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
            submitted =  (result_data.get("ca1Abs", False) == True) or (result_data.get("ca2Abs", False) == True) or (result_data.get("examAbs", False) == True)
                        
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
                obj.ca1Abs = result_data.get("ca1Abs",obj.ca1Abs)
                obj.ca2Abs = result_data.get("ca2Abs",obj.ca2Abs)
                obj.examAbs = result_data.get("examAbs",obj.examAbs)
                obj.total = total
                obj.is_submitted = (total > 0.0 or submitted)
                obj.save()

            # ✅ If not exists → create
            else:
                student = school.students.filter(id=student_id).first()
                if not student:
                    raise serializers.ValidationError(f"Student with id {student_id} does not exist.")
                StudentResult.objects.create(
                    batch=batch,
                    student=student,
                    is_submitted = (total > 0.0 or submitted) ,
                    ca1= float(result_data.get("ca1", 0)),
                    ca2=float(result_data.get("ca2", 0)),
                    exam=float(result_data.get("exam", 0)),
                    ca1Abs = result_data.get("ca1Abs",False),
                    ca2Abs = result_data.get("ca2Abs",False),
                    examAbs = result_data.get("examAbs",False),
                    total=total
                )

        # 🔄 Update Batch Status
        total_students = len(class_students)
        
        filled_results = batch.scores.filter(is_submitted = True).count()
        if filled_results == 0 :
            batch.status = "EMPTY"
            batch.save()
            return batch
            
        if filled_results < total_students:
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
        ).prefetch_related(
        "terms",'sessions'    ,'classrooms'
        ).first()
        
        if not school:
            raise serializers.ValidationError(f"School with this details does not exist.")
        
        # teacher_id = validated_data.get("teacher")
        # teacher = school.teachers.filter(id=teacher_id).first() if teacher_id else None
        
        # validate class also 
        class_room = school.classrooms.filter(id=validated_data["class_room"]).first()
        if not class_room:
            raise serializers.ValidationError(f"ClassRoom with id {validated_data['class_room']} does not exist.")
        # validate term also
        term = school.terms.filter(id=validated_data["term"]).first()
        if not term:
            raise serializers.ValidationError(f"Term with id {validated_data['term']} does not exist.")
        session = school.sessions.filter(id=validated_data["session"]).first()
        if not session:
            raise serializers.ValidationError(f"Session with id {validated_data['session']} does not exist.")
        
        # 🔒 Validate Students Belong to Class
        class_students = school.students.filter(
            class_rooms__class_room__id = class_room.id,
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
        # validate if batch is not locked before allowing updates
        if batch.is_locked or batch.on_submit or batch.approved :
            raise serializers.ValidationError("This batch cannot be modified.")
        
        batch.save()
        
        
        
        # chars = []
        for result_data in charAndSkills:
            student_id = result_data["studentId"]
            student = class_students.filter(id=student_id).first()
            submitted = False 
            if not student:
                continue  # skip fake injection safely
            
            # check if any char is set 

            submitted = any(
                result_data.get(field, 0) > 0
                for field in [
                    "punctuality",
                    "honesty",
                    "neatness",
                    "leadership",
                    "handwriting",
                    "verbal_fluency",
                    "creativity",
                ]
            )
                    
            obj, _ = StudentCharacterSkill.objects.update_or_create(
                batch = batch,
                student=student,
                defaults={
                    'is_submitted' : submitted ,
                    "punctuality": result_data.get('punctuality'),
                    "honesty": result_data.get('honesty'),
                    "neatness": result_data.get("neatness"),
                    "leadership": result_data.get("leadership"),
                    "handwriting": result_data.get("handwriting"),
                    "verbal_fluency": result_data.get("verbal_fluency"),
                    "creativity": result_data.get("creativity")
                }
            )
        # get batch status 
        students_count = class_students.count()
        
        students_with_record = batch.charAndSkills.filter(is_submitted = True).count()
        
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
        fields = ["id","studentId","student_name","subject_name","subject_code","subject_credits","ca1", "ca1Abs","ca2",'ca2Abs', "exam",'examAbs', "total",'grade','remark']

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



class ReportSheetDetailSerializer(serializers.ModelSerializer):
    student = MiniStudentSerializer(read_only = True)
    scores = serializers.SerializerMethodField(read_only=True)
    skills = serializers.SerializerMethodField(read_only=True)
    termName = serializers.CharField(source = "term.name",read_only =True,default=None)
    sessionName = serializers.CharField(source = "session.name",read_only =True,default=None)
    className = serializers.CharField(source = "class_room.name",read_only =True,default=None)
    totalClassStudents = serializers.IntegerField(source="total_class_students",read_only =True)
    school = serializers.SerializerMethodField(read_only = True)
    template = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = ReportSheet
        fields = "__all__"
    
    def get_scores(self,obj):
        scores =  self.context['scores'] 
        return StudentResultReadSerializer(scores,many=True).data 
    
    def get_school(self,obj):
        school = obj.student.school 
        return MiniSchoolSerializer(school).data
    
    def get_template(self,obj):
        temp = obj.student.school.templates.filter(type="Report",isActive=True).first()
        return TemplatesSerializer(temp).data
    
    def get_skills(self,obj):
        skill =  self.context['skills'] 
        if not skill :
            return None
        return StudentCharacterSkillSerializer(skill).data
class ReportSheetListSerializer(serializers.ModelSerializer) :
    student = StudentSerializer(read_only = True)
    totalSubjects = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ReportSheet
        fields = "__all__"
    
    def get_totalSubjects(self,obj):
        scores =  self.context['scores'] 
        scores = scores.filter(
            student_id = obj.student.id,
        ).distinct('id').count()
        
        # return StudentResultReadSerializer(scores,many=True).data
        return scores
    
    # def get_scores(self,obj):
    #     scores =  self.context['scores'] 
    #     scores = scores.filter(
    #         student_id = obj.student.id,
    #     ) or []
    #     return StudentResultReadSerializer(scores,many=True).data
    
    # def get_skills(self,obj):
    #     skills =  self.context['skills'] 
    #     skill = skills.get(
    #         student_id = obj.student.id,
    #         batch__approved = True ,
    #     ) or None
        
    #     if not skill :
    #         return None
    #     return StudentCharacterSkillSerializer(skill).data
    
    
class ApprovalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRecord
        fields = "__all__"
    
   
