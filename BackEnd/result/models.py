from django.db import models
from academics.models import *
from student.models import Student
from teacher.models import Teacher
from teacher.models import Teacher
from school.models import School , Session , Term

# Create your models here.
# -----------------------------------------------------------------------------------------------  
#                                       Marks and Report Models
# -----------------------------------------------------------------------------------------------  
class ResultBatch(models.Model):
    class_room = models.ForeignKey(
        ClassRoom, 
        on_delete=models.CASCADE,
        related_name="result_batches"
    )

    subject = models.ForeignKey(
            Subject,
        on_delete=models.CASCADE,
        related_name="result_batches"
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="result_batches"
    )

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="result_batches"
    )

    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name="result_batches"
    )

    status = models.CharField(
        max_length=10,
        choices=[
            ("EMPTY", "Empty"),
            ("PARTIAL", "Partial"),
            ("COMPLETE", "Complete"),
        ],
        default="EMPTY",
    )

    is_uploaded = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    on_submit = models.BooleanField(default=False)
    approved  = models.BooleanField( default= False) 

    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        unique_together = (
            "class_room",
            "subject",
            "session",
            "term",
        )
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} - {self.class_room} ({self.term})"

class StudentResult(models.Model):
    batch = models.ForeignKey(
        ResultBatch,
        on_delete=models.CASCADE,
        related_name="scores"
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="results"
    )

    ca1 = models.PositiveIntegerField(default=0)
    ca2 = models.PositiveIntegerField(default=0)
    exam = models.PositiveIntegerField(default=0)

    ca1Abs = models.BooleanField(default = False)
    ca2Abs = models.BooleanField(default = False)
    examAbs = models.BooleanField(default = False)
    is_submitted = models.BooleanField(default=False)
    
    total = models.PositiveIntegerField(default=0)
    grade = models.CharField(max_length=2)
    remark = models.CharField(max_length=50)

    class Meta:
        unique_together = ("batch", "student")

    def save(self, *args, **kwargs):
        self.total = self.ca1 + self.ca2 + self.exam
        self.grade, self.remark = self.calculate_grade()
        super().save(*args, **kwargs)

    def calculate_grade(self):
        if self.student.school.grading_system == 'standard':
            if self.total >= 75:
                return "A", "Excellent"
            elif self.total >= 65:
                return "B", "Very Good"
            elif self.total >= 50:
                return "C", "Credit"
            elif self.total >= 40:
                return "D", "Pass"
            return "F", "Fail"
        else:
            # Implement custom grading logic if needed
            return "N/A", "No Remark"

    def __str__(self):
        return f"{self.student} - {self.batch}"

class ReportSheet(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="report_sheets")
    
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="report_sheets")
    term = models.ForeignKey(Term, on_delete=models.SET_NULL,null=True, related_name="report_sheets")
    session = models.ForeignKey(Session, on_delete=models.SET_NULL,null=True, related_name="report_sheets")

    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0 )
    average_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0 )
    overall_grade = models.CharField(max_length=2, blank=True) 
    
    form_teacher_comment = models.TextField( blank=True )
    head_teacher_comment = models.TextField( blank=True )
    remarks = models.TextField(blank=True)
    
    position = models.IntegerField(null=True, blank=True)
    total_class_students = models.IntegerField(null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True) 
    
    approved  = models.BooleanField( default= False) 
    barcode_value = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
    )
    

    def __str__(self):
        return f"{self.student} - {self.term} - {self.total_marks} - {self.position} Report"
    

class CharacterBatch (models.Model) : 
    school = models.ForeignKey (School , on_delete=models.CASCADE, related_name="batch_skills")     
    class_room = models.ForeignKey (ClassRoom , on_delete=models.CASCADE, related_name="batch_skills")
    term = models.ForeignKey (Term , on_delete=models.SET_NULL,null=True, related_name="batch_skills")
    session = models.ForeignKey (Session , on_delete=models.SET_NULL,null=True, related_name="batch_skills")

    is_uploaded = models.BooleanField(default=False  ) 
    is_locked =   models.BooleanField(default=False  )
    on_submit =   models.BooleanField(default=False  )
    last_updated= models.DateTimeField(auto_now=True )
    created_at =  models.DateTimeField(auto_now_add=True )
    approved = models.BooleanField(default=False  ) 
    status = models.CharField(
        max_length=10,
        choices=[
            ("EMPTY", "Empty"),
            ("PARTIAL", "Partial"),
            ("COMPLETE", "Complete"),
        ],
        default="EMPTY",
    )

    class Meta :
        unique_together = (
            "class_room", 
            "session",
            "term" ,
        )
        ordering = ["-created_at"]
 
    def __str__(self):
        return f"{self.session.name} - {self.term} Char Report"
    
class StudentCharacterSkill(models.Model):
    batch = models.ForeignKey(CharacterBatch , on_delete=models.CASCADE, related_name = "charAndSkills")
    student = models.ForeignKey (Student , on_delete=models.CASCADE, related_name="skills")
    
    # characters 
    punctuality	 = models.IntegerField( blank=True, default=3)
    honesty = models.IntegerField( blank=True, default=3)	 
    neatness = models.IntegerField( blank=True, default=3)	 
    leadership  = models.IntegerField( blank=True, default=3) 	
    
    #skills 
    handwriting	 = models.IntegerField( blank=True, default=3 ) 
    verbal_fluency = models.IntegerField( blank=True, default=3 ) 	
    creativity = models.IntegerField( blank=True, default=3 )
    generated_at = models.DateTimeField( auto_now_add=True )
    is_submitted = models.BooleanField(default=False)
    
 
    def __str__(self):
        return f"{self.student} - {self.batch} Report"
    
class ApprovalRecord(models.Model) :
    school = models.ForeignKey (School , on_delete=models.CASCADE, related_name="approval_records")
    description	 = models.TextField()
    directorName = models.CharField(max_length=200, blank=True, )	 
    batchCount = models.IntegerField( blank=True,)	 
    timestamp = models.DateTimeField( auto_now_add=True )
 
    def __str__(self):
        return f"{self.description[:10]} - {self.directorName}"