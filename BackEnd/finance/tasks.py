from celery import shared_task
from django.db import transaction
from decimal import Decimal
from django.utils import timezone


from .models import StudentTransaction,PaymentInitiation
from .utils import net_balance_calculator ,get_trx_status
from student.models import Student, StudentClassEnrollment
from school.models import Session,Term


@shared_task
def generate_student_term_fees_task(session_id, term_id, filtered_student_ids):
    session  = Session.objects.get(id =session_id)
    term  = Term.objects.get(id =term_id)
    students = Student.objects.filter(id__in = filtered_student_ids)
    
    created_transactions = []

    class_fee_map = {}
    fees = session.school.class_fee_settings.prefetch_related("class_rooms")
    for fee in fees :
        for class_room in fee.class_rooms.all():
            class_fee_map[class_room.id] = fee.amount
            
    # 🔥 NEW: Get last transaction per student (1 query)
    
    last_trx_map = {}
    last_trxs = (
    StudentTransaction.objects
        .filter(student_id__in=filtered_student_ids)
        .order_by("student_id", "-created_at")
    )
    for trx in last_trxs:
        if trx.student_id not in last_trx_map:
            last_trx_map[trx.student_id] = trx
    
    existing = set(
        StudentTransaction.objects.filter(
            session=session,
            term=term
        ).values_list("student_id", "class_room_id")
    )
    # students = students.filter(user__is_active=True) 
    for student in students :
        if not hasattr(student,'class_rooms'): # to make sure student has ever been enrolled in a class 
            continue
        active_classes = student.class_rooms.filter(
            status__in=["active", "enrolled"]
        )

        if not active_classes.exists():
            continue # student has no any class activated  yet pass to the next  

        for enrollment in active_classes:
            class_id = enrollment.class_room.id

            if (student.id, class_id) in existing:
                continue # already fee assigned ,

            fee = class_fee_map.get(class_id)
            if not fee:
                continue # student class has ne fee settled so far  pass to the next  
            
            # lastTrx = StudentTransaction.filter(
            #     student = student
            # ).order_by("-created_at").first()
            
            lastTrx = last_trx_map.get(student.id)
            net_balance =  net_balance_calculator(lastTrx,fee,"FEE")
            status =       get_trx_status(lastTrx,fee,"FEE") 
            
            created_transactions.append (
                StudentTransaction(
                    student=student ,
                    class_room=enrollment.class_room ,
                    session=session,
                    term=term,
                    total_amount=float(fee),
                    amount_paid=0,
                    transaction_type="FEE",
                    description=f"Term fee for {enrollment.class_room.name}-{session.name}-{term.name}",
                    due_date=timezone.now() + timezone.timedelta(days=30),
                    net_balance = net_balance ,
                    status = status ,
                )
            )
    # BULK INSERT (very fast)
    StudentTransaction.objects.bulk_create(created_transactions)
    print("dones ",len(created_transactions))

    return len(created_transactions)


