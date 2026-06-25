from django.db.models import Sum, Avg,Prefetch
from .models import  ReportSheet, StudentResult ,ResultBatch ,CharacterBatch
from student.models import Student
from school.models import School , Session , Term
            
from django.utils import timezone 
from rest_framework.exceptions import ValidationError
from celery import shared_task
from django.db import transaction

from celery import shared_task
from django.db import transaction
import uuid

@shared_task(bind=True, name="generate_report_and_position", max_retries=2)
def generate_report_and_position(  self,  term_id,  session_id,  class_id,  school_id,):   
    with transaction.atomic():
        school = (
            School.objects
            .filter(id=school_id)
            .prefetch_related(
                "sessions",
                "terms",
                "classrooms",
                Prefetch(
                    "students",
                    queryset=Student.objects.filter(
                        school_id=school_id,
                        class_rooms__class_room_id=class_id,
                        class_rooms__status__in =["active", "enrolled"],
                    ).distinct(),
                    to_attr="class_students",
                ),
            )
            .first()
        )


        if not school:
            return {"error": "School not found."}

        students = school.class_students

        if not students:
            return []

        term = next(
            (t for t in school.terms.all()
             if t.id == term_id),
            None
        )

        session = next(
            (s for s in school.sessions.all()
             if s.id == session_id),
            None
        )

        class_room = next(
            (c for c in school.classrooms.all()
             if c.id == class_id),
            None
        )

        if not term:
            return  {"error": "Term not found."}

        if not session:
            return  {"error": "Session not found."}

        if not class_room:
            return {"error": "Class not found."}

        student_ids = [student.id for student in students]

        results = StudentResult.objects.filter(
            student_id__in=student_ids,
            batch__term_id=term_id,
            batch__session_id=session_id,
            batch__class_room_id=class_id,
        )

        # Approval check (ONE QUERY)
        if results.filter(
            batch__approved=False
        ).exists():
            return {"error": "Non Approved Results Found!"}

        # Aggregate per student (ONE QUERY)
        aggregates = (
            results.values("student_id")
            .annotate(
                total_marks=Sum("total"),
                average_marks=Avg("total"),
            )
        )

        aggregate_map = {
            row["student_id"]: row
            for row in aggregates
        }

        total_class_students = len(students)

        reports = []

        for student in students:

            data = aggregate_map.get(student.id)

            if not data:
                continue

            total = data["total_marks"]
            avg = data["average_marks"]

            if avg >= 70:
                grade = "A"
            elif avg >= 60:
                grade = "B"
            elif avg >= 50:
                grade = "C"
            elif avg >= 45:
                grade = "D"
            else:
                grade = "F"

            report, _ = ReportSheet.objects.update_or_create(
                student=student,
                class_room=class_room,
                term=term,
                session=session,
                defaults={
                    "total_marks": total,
                    "average_marks": avg,
                    "overall_grade": grade,
                    "total_class_students": total_class_students,
                },
            )
            if not report.barcode_value:
            # if report.barcode_value:
                value = f"c={school.tag}&c={student.id}&c={report.id}"
                report.barcode_value = value
                report.save(update_fields=["barcode_value"])

            reports.append(report)

        class_reports = list(
            ReportSheet.objects.filter(
                class_room=class_room,
                term=term,
                session=session,
            )
            .order_by("-total_marks")
        )

        position = 0
        last_score = None
        skip = 0

        for index, result in enumerate(
            class_reports,
            start=1,
        ):
            if result.total_marks != last_score:
                position = index
                position -= skip
                skip = 0
            else:
                skip += 1

            result.position = position
            last_score = result.total_marks

        ReportSheet.objects.bulk_update(
            class_reports,
            ["position"]
        )

        # return class_reports
    return {
    "success": True,
    "reports_generated": len(class_reports)
}