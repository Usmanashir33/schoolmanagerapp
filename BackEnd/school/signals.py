from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from authUser.models import User
from django.core.mail import send_mail

from django.core.exceptions import ValidationError
from .models import School, SchoolRole,Templates ,FinanceSettings,Term,Session ,SchoolPermission
import string
import random
from .custom_templates import CUSTOM_TEMPLATE_LIST

def generate_random_password(length=8):
    """Generate a random password with letters and digits"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length)) 
        
@receiver(post_save, sender=School) 
def create_finance_settings(sender, instance, created ,**kwargs):
    if created :
        FinanceSettings.objects.create(
            school=instance
        )
        Session.objects.bulk_create([
            Session(
                school=instance,
                name="2024/2025",
                is_current=False
            ),
            Session(
                school=instance,
                name="2025/2026",
                is_current=True
            ),
        ])
        Term.objects.bulk_create([
            Term(
                school = instance,
                name = "1st Term",
                is_current=False
            ),
            Term(
                school = instance,
                name = "2nd Term",
                is_current=True
            ),
        ])
        # create default permissions for the school
        SchoolPermission.objects.bulk_create([
            SchoolPermission(
                school = instance,
                name = "can_view_students",
                description = "Permission to view student information"
            ),
            SchoolPermission(
                school = instance,
                name = "can_add_students",
                description = "Permission to add new students"
            ),
            SchoolPermission(
                school = instance,
                name = "can_manage_students",
                description = "Permission to update/delete student information"
            ),
            SchoolPermission(
                school = instance,
                name = "students_management",
                description = "Permission to authorise student "
            ),
            
            SchoolPermission(
                    school = instance,
                    name = "can_view_teachers",
                    description = "Permission to view teacher information"
            ),
            SchoolPermission(
                    school = instance,
                    name = "can_add_teachers",
                    description = "Permission to add new teachers"
            ),
            SchoolPermission(
                    school = instance,
                    name = "can_manage_teachers",
                    description = "Permission to add new teachers"
            ),
            SchoolPermission(
                    school = instance,
                    name = "teachers_management",
                    description = "Permission to add authorise teachers"
            ),
            
            
            SchoolPermission(
                    school = instance,
                    name = "can_manage_teachers",
                    description = "Permission to update/delete teacher information"
            ),
                SchoolPermission(
                        school = instance,
                        name = "can_view_staffs",
                        description = "Permission to view staff information"
                ),
                SchoolPermission(
                        school = instance,
                        name = "can_add_staffs",
                        description = "Permission to add new staffs"
                ),
                SchoolPermission(
                        school = instance,
                        name = "can_manage_staffs",
                        description = "Permission to update/delete staff information"
                ),
                SchoolPermission(
                        school = instance,
                        name = "staffs_management",
                        description = "Permission to authorise staffs "
                ),
                # managing school permissions
                SchoolPermission(
                        school = instance,
                        name = "can_manage_school",
                        description = "Permission to manage school information and settings"
                ),
                # manage academic settings permissions
                SchoolPermission(
                        school = instance,
                        name = "can_manage_academics",
                        description = "Permission to manage academic settings like sessions, terms, grading system etc"
                ),
                # managin finance permissions
                SchoolPermission(
                        school = instance,
                        name = "can_manage_finance",
                        description = "Permission to manage finance settings and transactions"
                ),
                # accepting or regecting payments 
                SchoolPermission(
                    school = instance,
                    name = "can_manage_payments",
                    description = "Permission to manage pending payment transactions and accept or reject payments"
                ),
                # can approve or reject result 
                SchoolPermission(
                        school = instance,
                        name = "can_manage_results",
                        description = "Permission to manage pending student results and approve or reject results"
                ),
                # add and get results permissions
                SchoolPermission(
                        school = instance,
                        name = "can_add_results",
                        description = "Permission to add student results"
                ),
                SchoolPermission(
                        school = instance,
                        name = "can_view_results",
                        description = "Permission to view student results"
                ),
        ])
        
        # create school roles 
        SchoolRole.objects.bulk_create([
            SchoolRole(
                school = instance,
                name = "Director",
                description = "School director with full permissions"
            ),
            SchoolRole(
                school = instance,
                name = "Teacher",
                description = "School teacher with limited permissions"
            ),
            SchoolRole(
                school = instance,
                name = "Staff",
                description = "School staff with limited permissions"
            ),
            # accountaant 
            SchoolRole(
                school = instance,
                name = "Accountant",
                description = "School accountant with permissions to manage finance and payments"
            ),
            # registaror 
            SchoolRole(
                school = instance,
                name = "Registrar",
                description = "School registrar with permissions to manage students and academics"
            ),
        ])
        
        