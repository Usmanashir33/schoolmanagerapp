from django.db import transaction
from decimal import Decimal
from django.utils import timezone


from .models import StudentTransaction,PaymentInitiation
from student.models import Student, StudentClassEnrollment
from school.models import Session,Term

def get_active_class_rooms(self, obj) : 
    # get enrollments for the student with only active or enrolled status and eturn the class ids 
    enrollments = StudentClassEnrollment.objects.filter(student=obj, status__in = ['active', 'enrolled'])
    return [enrollment.class_room.id for enrollment in enrollments]
    
def net_balance_calculator(net_balance, new_amount, operation):
    previous_balance = float(net_balance) if net_balance else 0

    if operation == "FEE":
        return previous_balance - float(new_amount)

    elif operation in ["PAYMENT", "REFUND"]:
        return previous_balance + float(new_amount)

def get_trx_status(last_balance,currentFee,operation) :
    if not last_balance :
        return "UNPAID"
    
    if operation == "FEE" : # fee is negative 
        remaining = (float(last_balance) -  float(currentFee))
        if   remaining >=  0 :
            return "PAID"
        
        elif remaining  <  0 and  remaining >  float(last_balance) :
            return "PARTIAL"
        
        else :
            return "UNPAID"
        
    elif operation in  ["PAYMENT","REFUND"] :
        float(last_balance) + float(currentFee)
        return 'UNPAID'

from django.db import transaction
from django.utils import timezone
from school.models import School


@transaction.atomic
def process_payment(payment_ids, valid_school_id, action, note, resolver):
    # school = School.objects.filter(id = valid_school_id).first()
    pending_payments = PaymentInitiation.objects.filter(
        school__id =valid_school_id,
        status="PENDING",
        id__in=payment_ids
    ).prefetch_related("students")

    processed  = []

    # REJECT
    if action == "REJECT":
        for payment in pending_payments :
            payment.status = "REJECTED"
            payment.note = (payment.note or "") + f"\n{note}"
            payment.resolved_by = resolver
            payment.save()
            processed.append(str(payment.id))
        return processed

    # APPROVE
    for payment in pending_payments :

        remaining_amount = float( payment.total_amount )

        students = payment.students.all()

        for student in students:
            if remaining_amount <= 0: # the amount in the batch is finished 
                break

            # LAST TRANSACTION ONLY
            last_trx = (
                StudentTransaction.objects
                .filter(student=student)
                .order_by("-created_at")
                .first()
            )
            unpaid_fees =  (
                StudentTransaction.objects
                .filter(student=student,transaction_type__in=["FEE",], status__in=["UNPAID","PARTIAL"])
                .order_by("created_at")
            )

            # no previous trx
            if not last_trx :
                # continue
                pass

            old_balance = float(last_trx.net_balance if last_trx else 0 )

            # skip students without debt now  all all debts settled then return to it 
            if old_balance >= 0:
                continue

            debt = abs(old_balance)

            # FULL SETTLEMENT
            if remaining_amount >= debt:
                payment_applied = debt

            # PARTIAL SETTLEMENT
            else:
                payment_applied = remaining_amount

            # NEW RUNNING BALANCE
            new_balance = old_balance + payment_applied

            # CREATE NEW PAYMENT TRANSACTION
            StudentTransaction.objects.create(
                student=student,
                session=payment.session,
                term=payment.term,
                payment_source = payment ,

                transaction_type="PAYMENT",

                description=f"Payment approved by {resolver}",

                total_amount=0,

                amount_paid = payment_applied,

                net_balance=new_balance,

                status="PAID" if new_balance >= 0 else "PARTIAL",

            )
            # reduce available money
            remaining_amount -= payment_applied
            
            # LOOP THE FEES TO UPDATE BASE ON THE PAYMENT APPLIED \
            payment_amount = payment_applied 
            for fee in unpaid_fees :
                if payment_amount <= 0 :
                    break 
                
                fee_remainder  = float(fee.total_amount) - float(fee.amount_paid) #
                if payment_amount >= fee_remainder : # PAID 
                    settler = fee_remainder 
                    fee.amount_paid = float(fee.amount_paid) +  settler
                    fee.status = "PAID"
                    fee.payment_source =payment
                else : # PARTIAL 
                    settler = payment_amount
                    fee.amount_paid  = float(fee.amount_paid) +  settler
                    fee.status = "PARTIAL"
                    fee.payment_source =payment
                fee.save() 
                payment_amount -= settler 
                
            
            
        # students payment finished with all their last balance 
        # check if there is remaining add to the first student 
        if remaining_amount > 0 :
            for student in students:
                if remaining_amount <= 0: # the amount in the batch is finished 
                    break

                # LAST TRANSACTION ONLY
                last_trx = (
                    StudentTransaction.objects
                    .filter(student=student)
                    .order_by("-created_at")
                    .first()
                )

                # no previous trx
                if not last_trx :
                    # continue
                    pass

                old_balance = float(last_trx.net_balance if last_trx else 0 )
                payment_applied = remaining_amount 

                # NEW RUNNING BALANCE
                new_balance = old_balance + payment_applied

                # CREATE NEW PAYMENT TRANSACTION
                StudentTransaction.objects.create(
                    student=student,
                    session=payment.session,
                    term=payment.term,
                    payment_source = payment ,
                    transaction_type="PAYMENT",
                    description=f"Excess payment stored as student credit ",
                    total_amount=0,
                    amount_paid = payment_applied,
                    net_balance=new_balance,
                    status="PAID",
                )
                # reduce available money
                remaining_amount -= payment_applied

    payment.status = "APPROVED"
    payment.note = (payment.note or "") + f"\n{note}"

    # optional
    payment.resolved_by = resolver 

    payment.save()

    processed.append(str(payment.id))

    return processed