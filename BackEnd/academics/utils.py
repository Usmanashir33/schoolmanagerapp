from django.db import transaction
from django.db.models  import Q
from django.utils import timezone 
import time 

from student.models import (
    StudentClassEnrollment
)


class ClassRoomServices :

    @staticmethod
    @transaction.atomic
    def promote_students(old_class,new_class, session,promotion_log) :
        
        enrollments = StudentClassEnrollment.objects.select_related (
            "student"
        ).filter(
            class_room__id= old_class.id,
            status__in = ["active", "enrolled"]
        )

        promoted_count = 0

        for enrollment in enrollments:

            existing = StudentClassEnrollment.objects.filter(
                student_id=enrollment.student.id,
                class_room__id =new_class.id,
                session_id=session.id,
                status__in=["active", "enrolled"]
            ).exists()

            if existing:
                continue

            enrollment.status = "promoted"
            enrollment.save(
                update_fields=["status"]
            )
            StudentClassEnrollment.objects.create( 
                student_id=enrollment.student.id,
                class_room__id=new_class.id,
                session_id=session.id ,
                status = "active"
            )
            promoted_count += 1
            promotion_log.promoted_students = promoted_count
            promotion_log.save()

        return promoted_count
    
    @staticmethod
    @transaction.atomic
    def transfer_students(students,to_class,from_class,session): 
        for student in students :
            status = 'enrolled'
            if from_class : 
                # remove student from current class 
                status = ' active ' 
                StudentClassEnrollment.objects.filter(Q(student=student, class_room=from_class), Q(status__in =['active','enrolled']) ).update(status='transfered', date_left = timezone.now())
            # add student to new class 
            StudentClassEnrollment.objects.create(student=student, class_room=to_class, status=status,session=session)
        
        return students