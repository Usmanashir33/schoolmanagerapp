from django.core.cache import cache
from django.db import transaction
from django.db.models  import Q
from django.utils import timezone 
import time 

from academics.models import TeachingAssignment
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
    def transfer_students(students, to_class, from_class):
        student_ids = list(
            students.values_list("id", flat=True)
        )
        now = timezone.now()

        if from_class:
            StudentClassEnrollment.objects.filter(
                student__id__in=student_ids,
                class_room=from_class,
            ).update(
                status="transferred",
                date_left=now
            )

            status = "active"
        else:
            status = "enrolled"

        StudentClassEnrollment.objects.bulk_create([
            StudentClassEnrollment(
                student=student ,
                class_room=to_class ,
                status=status ,
            )
            for student in students
        ])

        cache.delete_pattern(
            f"academics_{to_class.section.school.id}_*"
        )

        return students
    
    @staticmethod
    @transaction.atomic
    def enroll_students(students,to_class): 
        StudentClassEnrollment.objects.bulk_create(
            (
                StudentClassEnrollment(
                    student=student,
                    class_room=to_class,
                    status="enrolled"
                )
                for student in students
            ),
            batch_size=1000
        )
        cache.delete_pattern(
            f"academics_{to_class.section.school.id}_*"
        )
        return students
    
    @staticmethod
    @transaction.atomic
    def subjects_assign(school,cls, mappings) :
        # Implementation for assigning subjects to a class
        TeachingAssignment.objects.bulk_create(
            (
                TeachingAssignment(
                    subject=mapping["subject"],
                    teacher=mapping["teacher"],
                    classroom=cls,
                    school=school
                )
                for mapping in mappings
            ),
            batch_size=1000
        )
        
        cache.delete_pattern(
            f"academics_{school.id}_*"
        )
    @staticmethod
    @transaction.atomic
    def subjects_re_assign(school,mappings) :
        # Implementation for re_assigning subjects to a class
        to_update = []
        for mapping in mappings :
            assignment = mapping.get("assignment")
            if assignment :
                assignment.teacher = mapping.get("teacher")
                to_update.append(assignment)
        TeachingAssignment.objects.bulk_update(
            to_update,
            ['teacher'],
            batch_size=1000
        )
        cache.delete_pattern(
            f"academics_{school.id}_*"
        )