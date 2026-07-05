
from core.formatters import format_serializer_errors
from core.formatters import format_serializer_errors
from core.permissions import ParentUserPermission
from core.websocketutils import signal_sender
from school.permissions import HasSchoolPermission,SchoolPermissions
from django.core.cache import cache
from core.custom_pegination import CustomPagination15
from rest_framework.exceptions import ValidationError

from django.db.models import Prefetch, Prefetch, Sum, DecimalField ,Q ,OuterRef, Subquery
from django.db.models.functions import Coalesce
import json 

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from school.models import School, Session, Term
from staff.models import Staff
from .models import ClassFeeSetting, PaymentInitiation ,StudentTransaction
from academics.models import ClassRoom
from student .models import StudentClassEnrollment ,Student
from .utils import process_payment
from .tasks import generate_student_term_fees_task 

from .serializers import SchoolFeeSerializer,ClassConfiguredSerializer,StudentsTrxsSerializer
from .serializers import StudentLedgerSerializer ,MiniStudentSerializer,PaymentInitiationSerializer,PaymentInitiationReadSerializer


class ParentPaymentsView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        ParentUserPermission,
    ]

    def get(self, request, school_id):   
        try:
            # 1. Fetch valid school environment
            valid_school = School.objects.filter(id=school_id).first() 
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)

            # 2. Check localized Cache layer (Isolated per Parent User to protect multi-tenant caching)
            cache_key = f"pendingpayments_{school_id}_user_{request.user.id}"
            try:
                cached_response = cache.get(cache_key)
                if cached_response:
                    # pass
                    return Response(cached_response, status=status.HTTP_200_OK)
            except:
                pass

            # 💡 SECURITY FIX 1: Isolate the guardian's specific children in this school
            guardian_students_queryset = Student.objects.filter(
                school=valid_school,
                guardian__user_id=request.user.id
            )

            # 💡 SECURITY FIX 2: Securely query payment data & lock the M2M prefetch boundary
            payms = (
                valid_school.payment_initiations
                .filter(students__in=guardian_students_queryset)  # Filters the outer table securely
                .select_related("session", "term")
                .prefetch_related(
                    Prefetch(
                        'students',
                        queryset=guardian_students_queryset  # 🔒 MASKS out other children from the query
                    )
                ).order_by('-date_initiated')
                .distinct()  # Eliminates duplicate entries caused by Many-to-Many joins
            )
            # 4. Serialize dataset safely
            pendingPayments = PaymentInitiationSerializer(payms, many=True)
            resp = {"success": "allPayments", "allPayments": pendingPayments.data}
            
            # 5. Populate cache layer
            try:
                cache.set(cache_key, resp, timeout=5 * 60)
            except:
                pass
                
            return Response(resp, status=status.HTTP_200_OK)

        except Exception as e:
            # You can log 'e' here if needed during debug development
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
class ParentStudentPaymentView(APIView) :
    permission_classes = [
        permissions.IsAuthenticated,
        ParentUserPermission,
    ]
    def post(self, request):   ## log payment when the payment is made
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            
            #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(id=school_id).first()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            
            finance_staffs = Staff.objects.filter(
                school_id=school_id,
                user__school_role__permissions__name = "can_manage_payments",
            ).distinct().values_list('user_id', flat=True)
            staffIds = list(finance_staffs) + [valid_school.director.user.id]  # Include director's user ID
            if not staffIds :
                return Response({"error": "No Finance Staff Found"}, status=status.HTTP_200_OK)
            
            serializer = PaymentInitiationSerializer( data=request.data, context={"request":request}) 
            if serializer.is_valid() :
                try :
                    serializer.save()
                    # send to director websocket now 
                    # loof and send to this staff
                    for staff_id in staffIds :
                        staff_room = f"room{staff_id}"
                        signal_data = {
                            "newPendingPayment":serializer.data,
                            "type" : "send_response1"
                        }
                        signal_sender(staff_room,signal_data)
                    
                    return Response({
                    "success": "Payment Logged Successfully",
                    "newPendingPayment": serializer.data
                }, status=status.HTTP_200_OK)
                except ValidationError as e:
                    return Response({"error": e.detail }, status=status.HTTP_200_OK)
                
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)