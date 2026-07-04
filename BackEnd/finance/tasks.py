from celery import shared_task
from django.db import transaction
from decimal import Decimal
from django.utils import timezone


from .models import StudentTransaction,PaymentInitiation
from .utils import net_balance_calculator ,get_trx_status
from student.models import Student, StudentClassEnrollment
from school.models import Session,Term,School
from django.core .cache import cache

@shared_task
def generate_student_term_fees_task(school_id, session_id, term_id, class_ids):

    school = School.objects.filter(id=school_id).prefetch_related(
        'terms', 'sessions', 'classrooms', 'class_fee_settings__class_rooms'
    ).first()

    term = school.terms.get(id=term_id)
    session = school.sessions.get(id=session_id)

    classrooms = school.classrooms.filter(id__in=class_ids)

    classes_students = Student.objects.filter(
        user__is_active=True,
        school=school,
        class_rooms__class_room__id__in=class_ids,
        class_rooms__status__in=['active', 'enrolled']
    ).prefetch_related("class_rooms__class_room").order_by("id").distinct("id")
    
    # ✅ FIX: Extract raw IDs into a list to prevent conflicting SQL subqueries
    student_ids = list(classes_students.values_list('id', flat=True))

    # ✅ Fee map
    class_fee_map = {}
    for fee in school.class_fee_settings.all():
        for cr in fee.class_rooms.all():
            class_fee_map[str(cr.id)] = fee.amount

    # ✅ Last transactions (Now safely using the extracted list of IDs)
    last_trxs = (
    StudentTransaction.objects
        .filter(student_id__in=student_ids) # Using student_id__in with raw IDs
        .order_by("student_id", "-created_at")
        .distinct("student_id")
    )

    old_last_trx_netbalances_map = {}
    for trx in last_trxs:
        if not old_last_trx_netbalances_map.get(trx.student_id): # optimization: use student_id directly
            old_last_trx_netbalances_map[trx.student_id] = trx.net_balance or 0

    latest_trx_netbalances_map = {}

    # ✅ Existing logs (Now safely using the extracted list of IDs)
    existing = set(
        StudentTransaction.objects.filter(
            session=session,
            term=term,
            class_room__in=classrooms,
            student_id__in=student_ids
        ).values_list("student__id", "class_room__id")
    )

    # ✅ Group students per class
    from collections import defaultdict
    class_students_map = defaultdict(list)

    for student in classes_students :
        for cr in student.class_rooms.all():
            if str(cr.class_room_id) in class_ids and cr.status in ['active', 'enrolled']:
                class_students_map[str(cr.class_room_id)].append(student)

    created_transactions = []

    # ✅ Main logic
    for cls in classrooms:
        fee = class_fee_map.get(str(cls.id))
        if not fee:
            continue
        stdts = class_students_map.get(str(cls.id), []) 

        for student in stdts :

            if (student.id, cls.id) in existing:
                continue

            last_netbalance = latest_trx_netbalances_map.get(
                student.id,
                old_last_trx_netbalances_map.get(student.id, 0)
            )

            net_balance = net_balance_calculator(last_netbalance, fee, "FEE")
            status = get_trx_status(last_netbalance, fee, "FEE")

            created_transactions.append(
                StudentTransaction(
                    student=student,
                    class_room=cls,
                    session=session,
                    term=term,
                    total_amount=float(fee),
                    amount_paid=0,
                    transaction_type="FEE",
                    description=f"Term fee for ⟪{cls.name}⟫» {session.name}●{term.name}",
                    due_date=timezone.now() + timezone.timedelta(days=30),
                    net_balance=net_balance,
                    status=status,
                )
            )

            latest_trx_netbalances_map[student.id] = net_balance
        StudentTransaction.objects.bulk_create(created_transactions)
        created_transactions = []

    return len(created_transactions)
