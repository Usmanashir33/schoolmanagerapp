from django.shortcuts import render
from django.db.models import FloatField
from core.emails.email_templates.emails import generate_otp_email,generate_login_email,generate_registration_email
from core.emails.email_templates.emails import generate_school_update_email,generate_school_delete_email
from core.tasks import send_html_email,send_ordinary_sms
from school.permissions import HasSchoolPermission,SchoolPermissions
from django.core.cache import cache
from core.custom_pegination import CustomPagination15


from core.formatters import format_serializer_errors
from core.permissions import DirectorUserPermission
from core.serializers import DirectorSchoolSerializer , DirectorSerializer
from rest_framework.exceptions import ValidationError
from core.utils.otp_generators import generate_5_otp
from core.websocketutils import signal_sender

from django.db.models import Sum, DecimalField ,Q ,OuterRef, Subquery
from django.db.models.functions import Coalesce
import json 


from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from school.models import School, Session, Term
from .models import ClassFeeSetting, PaymentInitiation ,StudentTransaction
from academics.models import ClassRoom
from student .models import StudentClassEnrollment ,Student
from .utils import process_payment
from .tasks import generate_student_term_fees_task 

from .serializers import SchoolFeeSerializer,ClassConfiguredSerializer,StudentsTrxsSerializer
from .serializers import StudentLedgerSerializer ,MiniStudentSerializer,PaymentInitiationSerializer,PaymentInitiationReadSerializer


class StudentLedgerView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self, request,school_id,student_id):  
        try:
             #--------------- validate director actions -------------------
            valid_school = School.objects.filter(id=school_id).first() 
            if not valid_school:
                return Response({"error": "Invalid School data"}, status=status.HTTP_200_OK)
            cache_key = f"studentLedger_{school_id}_{student_id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            student = Student.objects.filter(
                id = student_id ,
                school = valid_school ,
            ).first()
            if not student  : 
                return Response({"error": "Invalid Student data"}, status=status.HTTP_200_OK)
                
            strxs = StudentTransaction.objects.filter(
                # class_room__section__school = valid_school ,
                student = student
            ).order_by("-created_at")
            
            student_data = MiniStudentSerializer(student).data
            ledgerEntries = StudentLedgerSerializer(strxs,many=True).data
            resp ={"success": "student Ledger",'studentLedger':{"student":student_data,'ledgerEntries':ledgerEntries}}
            try:
                cache.set(cache_key,resp,timeout=5*60)
            except :
                pass
            return Response( resp, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

class SearchPaymentView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_FINANCE]
    def get(self, request,school_id,ref_number):   
        try:
            # valid_school = School.objects.filter(id=school_id).first() 
            # if not valid_school:
            #     return Response({"error": "Invalid School data"}, status=status.HTTP_200_OK)
            
            payment = PaymentInitiation.objects.filter(
                ref_number = ref_number ,
                school__id = school_id ,
            )
            data = PaymentInitiationReadSerializer(payment,many=True).data
            return Response({"success": "match found ",'searchResults':data}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
class PendingPaymentsView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_PAYMENTS]
    def get(self,request,school_id):   
        try:
            valid_school = School.objects.filter(id=school_id).prefetch_related(
                "payment_initiations"
            ).first() 
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            cache_key = f"pendingpayments_{school_id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            # get pending request data here 
            paym = valid_school.payment_initiations.prefetch_related('students').select_related("session",'term')
            pendings = paym.filter(status = "PENDING").order_by('-date_initiated')
            rejected = paym.filter(status = "REJECTED").order_by('-date_resolved')[:15]
            appoved =  paym.filter(status = "APPROVED").order_by('-date_resolved')[:15]
            
            pendingPaymentsList = [*pendings,*rejected,*appoved]
            pendingPayments = PaymentInitiationSerializer(pendingPaymentsList,many=True)
            resp ={"success": "allPayments", "allPayments":pendingPayments.data}
            try :
                cache.set(cache_key,resp,timeout=5*60)
            except :
                pass
            return Response(resp, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
            
class FinanceDashbordAllStudentsTrxView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_FINANCE]
    def get(self, request,school_id,session,term,type):   
        try:
            page = request.query_params.get("page", 1)
            cache_key = f"financedashbordstudenttrxs_{school_id}_{session}_{term}_{type}_{page}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    # pass
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            valid_school = School.objects.filter(id=school_id).prefetch_related(
                "sessions",'terms'
                ).first()  
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            
            session  = valid_school.sessions.filter(id = session).first()
            term  = valid_school.terms.filter(id =term).first() 
            if not term or not term :
                return Response({"error": "Invalid Session/Term"}, status=status.HTTP_200_OK)
            # Start by checking types 
            strxs = StudentTransaction.objects.filter(
                class_room__school__id = school_id ,
                term = term ,
                session = session,
            ).select_related(
                'student','payment_source'
            )
            #---------------------------paid-----------------------------------------------
            total_paid = strxs.filter(status__in  = ['PAID',])
            tp = total_paid.aggregate(
                total=Coalesce(Sum('total_amount'), 0, output_field=DecimalField())
            )
            paid_count = total_paid.distinct("student_id").count()
            
            #---------------------------unpaid-----------------------------------------------
            total_unpaid = strxs.filter(status__in  = ['UNPAID',])
            tup=total_unpaid.aggregate(
                total=Coalesce(Sum('total_amount'), 0, output_field=DecimalField())
            )
            unpaid_count = total_unpaid.distinct("student_id").count()
            
            #---------------------------partiallypaid-----------------------------------------------
            total_partial = strxs.filter(status__in  = ['PARTIAL',])
            tpar =total_partial.aggregate(
                total=Coalesce(Sum('total_amount'), 0, output_field=DecimalField())
            )
            partial_count = total_partial.distinct("student_id").count()
            
            # -------------------------------------Display Data---------------------------------------
            type == type.upper()
            trxs = strxs.filter(status__in  = [type,]).order_by(
                    "student_id",
                    "-created_at"
                ).distinct("student_id")
            paginator = CustomPagination15()

            paginated_trxs = paginator.paginate_queryset(
                trxs,
                request
            )
            data = StudentsTrxsSerializer(paginated_trxs,many = True ).data
            resp ={
                    
                    "total_paid" : tp['total'],
                    "paid_count":paid_count ,
                    
                    "total_unpaid" : tup['total'],
                    "unpaid_count" :unpaid_count ,
                    
                    "total_partial" : tpar['total'],
                    "partial_count":partial_count ,
                    
                    "data" : data,
            }
            resp=paginator.get_paginated_response({
                "success": "students trxs", 
                "paginated_data": resp
            })
            try :
                cache.set(cache_key,resp,timeout=5*60)
            except :
                pass
            return Response(resp, status=status.HTTP_200_OK)
        except :
                return Response({"error": "server failed"}, status=status.HTTP_200_OK)
class FinanceDashbordView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_FINANCE]
    def get(self, request,school_id,session,term,type):   
        try:
            cache_key = f"financedashbord_{school_id}_{session}_{term}_{type}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
             #--------------- validate director actions -------------------
            valid_school = School.objects.filter(id=school_id).prefetch_related(
                "sessions",'terms'
                ).first()  
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            
            session  = valid_school.sessions.filter(id = session).first()
            term  = valid_school.terms.filter(id =term).first() 
            if not term or not term :
                return Response({"error": "Invalid Session/Term"}, status=status.HTTP_200_OK)
            # Start by checking types 
            strxs = StudentTransaction.objects.filter( 
                class_room__school__id = school_id ,
                term = term ,
                session = session,
            ).select_related(
                'student','payment_source'
            )
            
            latest_trx_subquery = (
                StudentTransaction.objects
                .filter(student=OuterRef("student"))
                .order_by("-created_at")
            )
            latest_balance_subquery = (
                StudentTransaction.objects
                .filter(student=OuterRef("student"))
                .order_by("-created_at")
                .values("net_balance")[:1]
            )

            latest_trxs = StudentTransaction.objects.filter(
                id=Subquery(latest_trx_subquery.values("id")[:1])
            )
           

            total_net_bal = latest_trxs.aggregate(
                total_balance=Sum("net_balance")
            )["total_balance"] 
            
            #---------------------------Paid------------------------------------
            total_paid = strxs.filter(status__in  = ['PAID',])
            tp = total_paid.aggregate(
                total=Coalesce(Sum('total_amount'), 0,output_field=DecimalField())
            )
            paid_count = total_paid.distinct('student_id').count()
            
            #---------------------------Unpaid------------------------------------
            total_unpaid = strxs.filter(status__in  = ['UNPAID',])
            tup=total_unpaid.aggregate(
                total=Coalesce(Sum('total_amount'), 0, output_field=DecimalField())
            )
            unpaid_count = total_unpaid.distinct('student_id').count()
            
            #---------------------------Partial Paid------------------------------------
            total_partial = strxs.filter(status__in  = ['PARTIAL',])
            tpar =total_partial.aggregate(
                total=Coalesce(Sum('total_amount'), 0, output_field=DecimalField())
            )
            partial_count = total_partial.distinct('student_id').count()
            
            #----------------------------------Display Data------------------------
            if type == "PAID" :
                trxs = strxs.filter(status__in  = ['PAID',]).select_related(
                    'payment_source'
                ).order_by(
                    "student_id",
                    "-created_at"
                ).distinct(
                    "student_id"
                ).annotate(
                    current_net_balance=Subquery(latest_balance_subquery,output_field=FloatField())
                    
                )
                data = StudentsTrxsSerializer(trxs.all()[:15],many = True ).data
                resp ={
                    "total_net_balance" : total_net_bal ,
                    
                    "total_paid" : tp['total'],
                    "paid_count":paid_count ,
                    
                    "total_unpaid" : tup['total'],
                    "unpaid_count" :unpaid_count ,
                    
                    "total_partial" : tpar['total'],
                    "partial_count":partial_count ,
                    
                    "data" : data,
                    "type" : type
                }
                try :
                    cache.set(cache_key,{"success": "fully paid students", "dashbordData":resp},timeout=5*60)
                except :
                    pass
                return Response({"success": "fully paid students", "dashbordData":resp}, status=status.HTTP_200_OK)
            
            elif type == "PARTIAL" :
                trxs = strxs.filter(status__in  = ['PARTIAL',]).select_related(
                    'payment_source'
                ).order_by(
                    "student_id",
                    "-created_at"
                ).distinct(
                    "student_id"
                ).annotate(
                    current_net_balance=Subquery(latest_balance_subquery,output_field=FloatField())
                )
                data = StudentsTrxsSerializer(trxs.all()[:15],many = True ).data
                resp ={
                    "total_net_balance" : total_net_bal ,
                    
                    "total_paid" : tp['total'],
                    "paid_count":paid_count ,
                    
                    "total_unpaid" : tup['total'],
                    "unpaid_count" :unpaid_count ,
                    
                    "total_partial" : tpar['total'],
                    "partial_count":partial_count ,
                    "data" : data,
                    "type" : type
                }
                try :
                    cache.set(cache_key,{"success": "partially paid students", "dashbordData":resp},timeout=60*5)
                except :
                    pass
                return Response({"success": "partially paid students", "dashbordData":resp}, status=status.HTTP_200_OK)
            
            else :
                trxs = strxs.filter(status__in  = ['UNPAID',]).select_related(
                    'payment_source'
                ).order_by(
                        "student_id",
                        "-created_at"
                    ).distinct(
                        "student_id"
                    ).annotate(
                    current_net_balance=Subquery(latest_balance_subquery,output_field=FloatField())
                )
                data = StudentsTrxsSerializer(trxs.all()[:15],many = True).data # only 15 if we need much we click view more or search
                resp ={
                    "total_net_balance" : total_net_bal ,
                    
                    "total_paid" : tp['total'],
                    "paid_count":paid_count ,
                    
                    "total_unpaid" : tup['total'],
                    "unpaid_count" :unpaid_count ,
                    
                    "total_partial" : tpar['total'],
                    "partial_count":partial_count ,
                    "data" : data,
                    "type" : type
                }
                try :
                    cache.set(cache_key,{"success": "unpaid students", "dashbordData":resp},timeout=5*60)
                except :
                    pass
                return Response({"success": "unpaid students", "dashbordData":resp}, status=status.HTTP_200_OK)
            
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
class FeeStartEngineView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_FINANCE]
    def get(self, request,school_id,session,term):   ## get school fee setting
        try:
            cache_key = f"configured_classes_{school_id}_{session}_{term}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    pass
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            valid_school = School.objects.filter(id=school_id).prefetch_related('sessions','terms').first()  #.exists()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            
            session  = valid_school.sessions.filter(id = session).first()
            term  = valid_school.terms.filter(id =term).first() #.exists()
            
            if not term or not session :
                return Response({"error": "Invalid Session/Term "}, status=status.HTTP_200_OK)
            
            configured_classes = ClassRoom.objects.filter(
                school__id = valid_school.id ,
                student_fees__session__id = session.id,
                student_fees__term__id = term.id,
                student_fees__transaction_type = "FEE",
            ).prefetch_related("student_fees").distinct()
            
            data = ClassConfiguredSerializer(configured_classes ,many=True,context={ "term":term, 'session':session}).data
            # call the fee generator 
            resp = {"success": "configured classes","configured_classes":data}
            try :
                cache.set(cache_key,resp,timeout=3*60)
            except :
                pass
            return Response(resp, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
    
    def post(self, request):   ## set school fee for classes students 
        try:
            pin = request.data.get("pin")
            classesIds = request.data.get("classIds")
            
            school_id = request.data.get("school")
            session = request.data.get("session")
            term = request.data.get("term")
            
            #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
             #--------------- validate director actions -------------------
            valid_school = School.objects.filter(id=school_id).prefetch_related(
                "sessions",'terms','classrooms'
                ).first()  #.exists()
            if not valid_school:
                return Response({"error": "Invalid School/Director Entry"}, status=status.HTTP_200_OK)
            
            session  = valid_school.sessions.filter(id = session).first()
            term  = valid_school.terms.filter(id =term).first() #.exists()
            
            if not term or not session :
                return Response({"error": "Invalid Session or Term "}, status=status.HTTP_200_OK)
            valid_classIds = valid_school.classrooms.filter(id__in = classesIds).distinct().values_list("id",flat=True)
            # call the fee generator 
            # gen = generate_student_term_fees_task(school_id,session.id,term.id,list(valid_classIds))
            gen = generate_student_term_fees_task.delay(school_id,session.id,term.id,list(valid_classIds))
            if gen :
                try :
                    cache.delete_pattern(
                        f"financedashbord_{school_id}_*"
                    )
                    cache.delete_pattern(
                        f"configured_classes_{school_id}_*"
                    )
                    cache.delete_pattern(
                        f"financedashbordstudenttrxs_{school_id}_*"
                    )
                except :
                    pass
            return Response({"success": "fee is generating in the background \n for active students","generated":True}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
class StudentPaymentView(APIView) :
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, school_id, payment_id):   ## log payment when the payment is made
        try:
            valid_school = School.objects.filter(id=school_id).first()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            cache_key = f"paymentinit_{school_id}_{payment_id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            payment = PaymentInitiation.objects.filter(
                id = payment_id ,
                school = valid_school
            ).prefetch_related("students").select_related(
                'term','session'
                ).first()
            if not payment:
                return Response({"error": "payment not found!"}, status=status.HTTP_200_OK)
            
            serializer = PaymentInitiationReadSerializer(payment) 
            resp = {
                    "success": "Payment fetched Successfully",
                    "fetchedPayment": serializer.data
                }
            try:
                cache.set(cache_key,resp,timeout=5*60)
            except:
                pass
            return Response(resp, status=status.HTTP_200_OK)
                    
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
class StudentPaymentOnlyStaffView(APIView) :
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_PAYMENTS]
        
    def post(self, request):   ## log payment when the payment is made
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            
            #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(id=school_id) 
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
            #--------------- end  validate director actions -------------------
            serializer = PaymentInitiationSerializer( data=request.data, context={"request":request}) 
            if serializer.is_valid() :
                try :
                    serializer.save()
                    # send to director websocket now 
                    # not needed to send back to director or finance manager 
                    # director_room = f"room{director.user.id}"
                    # signal_data = {
                    #     "newPendingPayment":serializer.data,
                    #     "type" : "send_response1"
                    # }
                    # signal_sender(director_room,signal_data)
                    
                    return Response({
                    "success": "Payment Logged Successfully",
                    "newPendingPayment": serializer.data
                }, status=status.HTTP_200_OK)
                except ValidationError as e:
                    return Response({"error": e.detail }, status=status.HTTP_200_OK)
                
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
    def put(self, request):   # process pending payment
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            paymentIds = request.data.get("paymentIds")
            action = request.data.get("action") # APPROVE or REJECT
            reason = request.data.get("reason")
            resolver = f"{request.user.role}-{request.user.first_name}-{request.user.last_name}"
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(id=school_id) 
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
            resp = process_payment(paymentIds,school_id,action,reason,resolver)
            
            if resp is not None and len(resp) > 0 :
                nameField = 'approvedPayments' if action == "APPROVE" else "rejectedPayments"
                return Response({
                    "success": "Payment settled  Successfully",
                     nameField : json.dumps(resp)
                }, status=status.HTTP_200_OK)
            else : # payment processed or invalid 
                return Response({"error": "processed or invalid" }, status=status.HTTP_200_OK)
                
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
class SchoolFeeSettingsView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_SCHOOL]
    
    def post(self, request):   ## add new school fee setting
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            
             #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter( id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
             #--------------- end  validate director actions -------------------
            
            serializer = SchoolFeeSerializer(data=request.data,context = {"request":request})
            if serializer.is_valid() :
                try :
                    serializer.save()
                    return Response({
                    "success": "School fee setting added successfully",
                    "new_school_fees": serializer.data
                }, status=status.HTTP_200_OK)
                except ValidationError as e:
                    return Response({"error": e.detail }, status=status.HTTP_200_OK)
                
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
    def put(self, request,fee_id):   ## update school fee setting
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(id=school_id)
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            
            valid_fee_id = ClassFeeSetting.objects.filter(school=valid_school.first(), id=fee_id).first()  #.exists()
            if not valid_fee_id:
                return Response({"error": "Invalid School-Fee Entry"}, status=status.HTTP_200_OK)
             #--------------- end  validate director actions -------------------
            
            serializer = SchoolFeeSerializer(valid_fee_id, data=request.data, context = {"request":request})
            if serializer.is_valid() :
                try :
                    serializer.save()
                    return Response({
                    "success": "School fee setting updated successfully",
                    "updated_school_fees": serializer.data
                }, status=status.HTTP_200_OK)
                except ValidationError as e:
                    return Response({"error": e.detail }, status=status.HTTP_200_OK)
                
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
    def delete(self, request,school_id,fee_id,pin):   ## delete school fee setting
        try:
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(id=school_id) 
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            
            valid_fee_id = ClassFeeSetting.objects.filter(school=valid_school.first(), id=fee_id).first()  #.exists()
            if not valid_fee_id:
                return Response({"error": "Invalid Setting Selection"}, status=status.HTTP_200_OK)
             #--------------- end  validate director actions -------------------
            valid_fee_id.delete()
            return Response({
                    "success": "School fee setting deleted successfully",
                    "deleted_school_fees": { "id": fee_id }
                }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
