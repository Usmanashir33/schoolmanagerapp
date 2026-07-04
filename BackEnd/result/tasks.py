from django.db.models import Sum, Avg,Prefetch
from .models import  ReportSheet, StudentResult ,ResultBatch ,CharacterBatch,ReportRecord
from student.models import Student
from school.models import School , Session , Term
from .serializers import ReportSerializer
            
from django.utils import timezone 
from rest_framework.exceptions import ValidationError
from celery import shared_task
from django.db import transaction
from core.websocketutils import signal_sender
import logging
import  time 
from celery import shared_task
from django.db import transaction
import uuid
# views.py or any view file
from core.emails.email_templates.emails import generate_result_compilation_email
from core.tasks import send_html_email,send_ordinary_sms
logger = logging.getLogger(__name__)

def send_report_update(record):
    """Send websocket update to school room"""
    try:
        time.sleep(1) # simulate delay for better frontend experience
        room_name = f"school-{record.school_id}"
        data = {
            "type": "school_feeder2",
            "report_record": ReportSerializer(
                record
            ).data
        }
        signal_sender(room_name, data)
    except Exception as e:
        logger.error(
            f"Failed to send promotion websocket update: {str(e)}"
        )


@shared_task(bind=True, name="generate_report_and_position", max_retries=3)
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
                        class_rooms__session_id=session_id,
                        class_rooms__class_room_id=class_id,
                        class_rooms__status__in =["active", "enrolled"],
                    ).distinct(),
                    to_attr="class_students",
                ),
                Prefetch(
                    "batch_skills",
                    queryset=CharacterBatch.objects.filter(
                        session_id = session_id,
                        class_room_id = class_id,
                        approved = True,
                    ).distinct().all(),
                    to_attr="skills",
                ),
            )
            .first()
        )

        students = school.class_students
        if not students:
            status = 'FAILED'
            # send signal here pls 
            rr.updated_at = timezone.now()
            rr.status = status
            rr.save(update_fields=[ "updated_at", "status"])       
            # final websocket update
            send_report_update(rr)
            return {"error": "students not found."}

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

        if not term or not class_room or not session :
            status = 'FAILED'
            # send signal here pls 
            rr.updated_at = timezone.now()
            rr.status = status
            rr.save(update_fields=[ "updated_at", "status"])       
            # final websocket update
            send_report_update(rr)
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
        skills = school.skills 
        if not skills:
            return {"error": f"{class_room.name} Char&Skill form not approved!"}

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
        rr,created = ReportRecord.objects.get_or_create(
            school = school,
            class_room = class_room,
            session = session,
            term = term ,
            defaults = {'status':"PENDING"}
        )
        # send signal here 
        send_report_update(rr)
        
        started = 0

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
        if not started :
            # send signal here 
            status = 'GENERATING'
            rr.updated_at = timezone.now()
            rr.status = status

            rr.save(
                update_fields=[
                    "updated_at",
                    "status"
                ]
            )
            # final websocket update
            send_report_update(rr)
            started +=1
            # time.sleep(5)
            
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
        status = 'GENERATED'
        # send signal here pls 
        rr.updated_at = timezone.now()
        rr.status = status
        rr.save(update_fields=[ "updated_at", "status"])       
        # final websocket update
        send_report_update(rr)
        # send email here to the class master 
         # send the email 
        try:    
            form_teacher = class_room.form_teacher
            html_content = generate_result_compilation_email(
                form_teacher.full_name(), 
                class_room.name, 
            )
            send_html_email.delay(
                subject=f"{school.tag} ● Result Compilation" ,
                to_email=[form_teacher.email], 
                html_content=html_content
            )
        except Exception :
                    pass 

    return {
    "success": True,
    "reports_generated": len(class_reports)
}