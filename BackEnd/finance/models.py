import uuid
from django.db import models
from academics.models import ClassRoom
from school.models import School, Session, Term,School
from parent.models import Parents
from student.models import Student


import random
import string
from django.utils import timezone


def generate_payment_reference(tag):

    date_part = timezone.now().strftime("%Y%m%d")

    random_part = ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=6
        )
    )

    return f"PAY-{tag}-{date_part}-{random_part}"

class ClassFeeSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE,related_name='class_fee_settings')
    class_rooms = models.ManyToManyField(ClassRoom,blank=True, related_name='classfeesetting')
    name = models.CharField(max_length=100,blank=True,null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        unique_together = ('school', 'name') 
        pass

    def __str__(self):
        return f"{self.school} - {self.id}"

# when director initiate the fee for that term and session 
TRANSACTION_TYPE = [
        ('FEE', 'School Fee'),
        ('COMPENSATION', 'School Compensation'),
        ('REFUND', 'Refund'),
        ('ADJUSTMENT', 'Adjustment'),
        ('PAYMENT', 'Payment'),
    ]

class StudentTransaction(models.Model):  # student termly fee for a session and payment also 
    student = models.ForeignKey(Student, on_delete=models.CASCADE,related_name= "student_fees")
    class_room = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL , related_name='student_fees',
            blank=True, null=True) # not required in payment initiation but required for fee setting and payment allocation
    
    session = models.ForeignKey(Session , on_delete=models.SET_NULL , related_name='student_fees',
                                   blank=True, null=True)
    
    term = models.ForeignKey(Term, on_delete=models.SET_NULL , related_name='student_fees',
                                   blank=True, null=True)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2) # negative value for tremly fee 
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    net_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    payment_source = models.ForeignKey(
        "PaymentInitiation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE,blank=True, null=True)
    description = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("UNPAID", "Unpaid"),
            ("PARTIAL", "Partial"),
            ("PAID", "Paid")
        ],
        default="UNPAID"
    )

    due_date = models.DateTimeField(blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add=True)

class PaymentInitiation(models.Model): 
    PAYMENT_METHODS = [
        ('TRANSFER', 'Transfer'),
        ('CASH', 'Cash'),
        ('WALLET', 'Wallet'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False )
    ref_number= models.CharField(max_length=50,unique=True,blank=True)
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='payment_initiations' )
    
    # Store multiple students
    students = models.ManyToManyField(Student, blank=True)  #["id1", "id2"] 
    session = models.ForeignKey(Session, on_delete=models.CASCADE) 
    term = models.ForeignKey(Term, on_delete=models.CASCADE) 
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    note = models.TextField(null=True, blank=True)
    

    # parentFields 
    payer = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    account_number = models.CharField(max_length=20, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)


    wallet_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    date_initiated = models.DateTimeField(auto_now_add=True)
    date_resolved = models.DateTimeField(null=True, blank=True,auto_now=True)

    resolved_by = models.CharField(max_length=100, null=True, blank=True)  # or ForeignKey(Admin)

    def __str__(self):
        return f"{self.payer} - {self.status}"
    
    def save(self, *args, **kwargs):

        if not self.ref_number:
            self.ref_number = generate_payment_reference(self.school.tag)

        super().save(*args, **kwargs)
    
