from django.shortcuts import render
from core.emails.email_templates.emails import generate_otp_email,generate_login_email,generate_registration_email
from core.emails.email_templates.emails import generate_school_update_email,generate_school_delete_email
from core.tasks import send_html_email,send_ordinary_sms

from core.formatters import format_serializer_errors
from core.permissions import DirectorUserPermission
from core.serializers import SchoolSerializer , DirectorSerializer
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
from classroom.models import ClassRoom
from student .models import StudentClassEnrollment ,Student
from .utils import process_payment
from .tasks import generate_student_term_fees_task 

from .serializers import SchoolFeeSerializer,ClassConfiguredSerializer,DirectorFinanceDashbordSerializer
from .serializers import StudentLedgerSerializer ,MiniStudentSerializer,PaymentInitiationSerializer,PaymentInitiationReadSerializer


class StudentLedgerView(APIView):
    def get(self, request,school_id,student_id):   ## add new school fee setting
        try:
             #--------------- validate director actions -------------------
            valid_school = School.objects.filter(id=school_id).first() 
            if not valid_school:
                return Response({"error": "Invalid School data"}, status=status.HTTP_200_OK)
             # Start by checking types 
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
            return Response({"success": "student Ledger",'studentLedger':{"student":student_data,'ledgerEntries':ledgerEntries}}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

class DirectorSearchPaymentView(APIView):
    def get(self, request,school_id,ref_number):   
        try:
             #--------------- validate director actions -------------------
            valid_school = School.objects.filter(id=school_id).first() 
            if not valid_school:
                return Response({"error": "Invalid School data"}, status=status.HTTP_200_OK)
            
            payment = PaymentInitiation.objects.filter(
                ref_number = ref_number ,
                school = valid_school ,
            )
            data = PaymentInitiationReadSerializer(payment,many=True).data
            return Response({"success": "match found ",'searchResults':data}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
class DirectorPendingPaymentsView(APIView):
    permission_classes = [DirectorUserPermission]
    def get(self,request,school_id):   
        try:
            director = request.user.director
             #--------------- validate director actions -------------------
            valid_school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
            # get pending request data here 
            payments = PaymentInitiation.objects.filter(
                school = valid_school ,
            )
            pendings = payments.filter(status = "PENDING").order_by('-date_initiated')
            rejected = payments.filter(status = "REJECTED").order_by('-date_resolved')[:100]
            appoved =  payments.filter(status = "APPROVED").order_by('-date_resolved')[:100]
            
            pendingPaymentsList = [*pendings,*rejected,*appoved]
            pendingPayments = PaymentInitiationSerializer(pendingPaymentsList,many=True)
            return Response({"success": "allPayments", "allPayments":pendingPayments.data}, status=status.HTTP_200_OK)
        
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
            
class DirectorFinanceDashbordView(APIView):
    permission_classes = [DirectorUserPermission]
    def get(self, request,school_id,session,term,type):   ## add new school fee setting
        # try:
            director = request.user.director
             #--------------- validate director actions -------------------
            valid_school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
            session  = Session.objects.filter(id = session,school=valid_school).first()
            term  = Term.objects.filter(id =term,school = valid_school).first() #.exists()
            if not term or not term :
                return Response({"error": "Invalid Session/Term"}, status=status.HTTP_200_OK)
            # Start by checking types 
            strxs = StudentTransaction.objects.filter(
                class_room__section__school = valid_school ,
                term = term ,
                session = session,
            )

            latest_trx_subquery = (
                StudentTransaction.objects
                .filter(student=OuterRef("student"))
                .order_by("-created_at")
            )

            latest_trxs = StudentTransaction.objects.filter(
                id=Subquery(latest_trx_subquery.values("id")[:1])
            )

            total_net_bal = latest_trxs.aggregate(
                total_balance=Sum("net_balance")
            )["total_balance"]
            
            total_paid = strxs.filter(status__in  = ['PAID',])
            paid_count = total_paid.count()
            tp = total_paid.aggregate(
                total=Coalesce(Sum('total_amount'), 0, output_field=DecimalField())
            )
            
            total_unpaid = strxs.filter(status__in  = ['UNPAID',])
            unpaid_count = total_unpaid.count()
            tup=total_unpaid.aggregate(
                total=Coalesce(Sum('total_amount'), 0, output_field=DecimalField())
            )
            
            total_partial = strxs.filter(status__in  = ['PARTIAL',])
            partial_count = total_partial.count()
            tpar =total_partial.aggregate(
                total=Coalesce(Sum('total_amount'), 0, output_field=DecimalField())
            )
            if type == "PAID" :
                trxs = strxs.filter(status__in  = ['PAID',])
                data = DirectorFinanceDashbordSerializer(trxs,many = True ).data
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
                return Response({"success": "fully paid students", "dashbordData":resp}, status=status.HTTP_200_OK)
            
            elif type == "PARTIAL" :
                trxs = strxs.filter(status__in  = ['PARTIAL',])
                data = DirectorFinanceDashbordSerializer(trxs,many = True ).data
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
                return Response({"success": "partially paid students", "dashbordData":resp}, status=status.HTTP_200_OK)
            
            else :
                trxs = strxs.filter(status__in  = ['UNPAID',])
                data = DirectorFinanceDashbordSerializer(trxs,many = True).data
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
                return Response({"success": "unpaid students", "dashbordData":resp}, status=status.HTTP_200_OK)
            
        # except Exception as e :
            # return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
class DirectorFeeStartEngineView(APIView):
    permission_classes = [DirectorUserPermission]
    def get(self, request,school_id,session,term):   ## add new school fee setting
        try:
            director = request.user.director
             #--------------- validate director actions -------------------
            valid_school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
            session  = Session.objects.filter(id = session,school=valid_school).first()
            term  = Term.objects.filter(id =term,school = valid_school).first() #.exists()
            
            if not term or not term :
                return Response({"error": "Invalid Session/Term "}, status=status.HTTP_200_OK)
            
            configured_classes = ClassRoom.objects.filter(
                section__school = valid_school ,
                student_fees__session = session,
                student_fees__term = term,
                student_fees__transaction_type = "FEE",
            ).distinct()
            
            data = ClassConfiguredSerializer(configured_classes ,many=True,context={ "term":term, 'session':session}).data
            # call the fee generator 
            return Response({"success": "configured classes","configured_classes":data}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
    
    def post(self, request):   ## get school configured classes
        try:
            pin = request.data.get("pin")
            classesIds = request.data.get("classIds")
            
            school_id = request.data.get("school")
            session = request.data.get("session")
            term = request.data.get("term")
            
            director = request.user.director
            #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
             #--------------- validate director actions -------------------
            valid_school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not valid_school:
                return Response({"error": "Invalid School/Director Entry"}, status=status.HTTP_200_OK)
            
            session  = Session.objects.filter(id = session,school=valid_school).first()
            term  = Term.objects.filter(id =term,school = valid_school).first() #.exists()
            
            if not term or not term :
                return Response({"error": "Invalid Session or Term "}, status=status.HTTP_200_OK)
            
            valid_studentsIds = Student.objects.filter(
                    user__is_active=True,
                    class_rooms__class_room__section__school=valid_school,
                    class_rooms__class_room__id__in=classesIds,
                    class_rooms__status__in=['active', 'enrolled']
                ).distinct().values_list("id",flat=True)
            
            # call the fee generator 
            generated = generate_student_term_fees_task.delay(session.id,term.id,list(valid_studentsIds))
            
            return Response({"success": "fee is generating in the background","generated":True}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
class DirectorStudentPaymentView(APIView):
    permission_classes = [DirectorUserPermission]
    # parser_classes =[MultiPartParser,FormParser]
    
    def get(self, request, school_id, payment_id):   ## log payment when the payment is made
        # try:
            director = request.user.director
            
            #--------------- validate director actions -------------------
            valid_school = School.objects.filter(director_id = director.id, id=school_id).first()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            #--------------- end  validate director actions -------------------
            
            payment = PaymentInitiation.objects.filter(
                id = payment_id ,
                school = valid_school
            ).first()
            if not payment:
                return Response({"error": "payment not found!"}, status=status.HTTP_200_OK)
            
            serializer = PaymentInitiationReadSerializer(payment) 
            return Response({
                    "success": "Payment fetched Successfully",
                    "fetchedPayment": serializer.data
                }, status=status.HTTP_200_OK)
                    
        # except Exception as e :
            # return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
    def post(self, request):   ## log payment when the payment is made
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            director = request.user.director
            
            #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id) 
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
        
    def put(self, request):   ## log payment when the payment is made
        # try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            paymentIds = request.data.get("paymentIds")
            action = request.data.get("action") # APPROVE or REJECT
            reason = request.data.get("reason")
            director = request.user.director
            resolver = f"{request.user.role}-{request.user.first_name}-{request.user.last_name}"
            
            #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id) 
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            resp = process_payment(paymentIds,school_id,action,reason,resolver)
            print('resp: ', resp)
            
            #--------------- end  validate director actions -------------------
            if resp is not None and len(resp) > 0 :
                nameField = 'approvedPayments' if action == "APPROVE" else "rejectedPayments"
                return Response({
                    "success": "Payment settled  Successfully",
                     nameField : json.dumps(resp)
                }, status=status.HTTP_200_OK)
            else : # payment processed or invalid 
                return Response({"error": "processed or invalid" }, status=status.HTTP_200_OK)
                
        # except Exception as e :
            # return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
class DirectorSchoolFeeSettingsView(APIView):
    permission_classes = [DirectorUserPermission]
    def post(self, request):   ## add new school fee setting
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            director = request.user.director
            
             #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
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
            director = request.user.director
            
             #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
            valid_fee_id = ClassFeeSetting.objects.filter(school=valid_school.first(), id=fee_id).first()  #.exists()
            if not valid_fee_id:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
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
            director = request.user.director
            
             #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
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
        
        
# class DirectorClassTransferView(APIView):
#     permission_classes = [DirectorUserPermission]
    
#     def put(self, request):
#         try:
#             pin = request.data.get( "pin" )
#             school_id = request.data.get( "school" )
#             target_class_id = request.data.get("target_class_id")
#             current_class_id = request.data.get("current_class_id")
#             transfer_students_ids = request.data.get("transfer_students_ids")
#             print('transfer_students_ids: ', transfer_students_ids)
            
#             #--------------- validate director actions -------------------
            # director = request.user.director
            
#             if not request.user.pins.checkPin(pin) :
#                 return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
#             valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
#             if not valid_school:
#                 return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
#              #--------------- end  validate director actions -------------------
#             if not all([school_id, target_class_id, transfer_students_ids]):
#                 return Response(
#                     {"error": "Missing required fields"},
#                     status=status.HTTP_200_OK
#                 )
            
#             from_class = ClassRoom.objects.filter(id = current_class_id ).first()
#             to_class = ClassRoom.objects.filter(id=target_class_id ).first()  
#             # implement transfer logic 
#             if not to_class :
#                 return Response({"error": "Invalid class selection"}, status=status.HTTP_200_OK)  
            
#             students = Student.objects.filter(id__in=transfer_students_ids, school__id=school_id).all()
#             if not students :
#                 return Response({"error": "Invalid students data"}, status=status.HTTP_200_OK)  
            
#             for student in students:
#                 if from_class : 
#                     # remove student from current class 
#                     StudentClassEnrollment.objects.filter(Q(student=student, class_room=from_class), Q(status='active') | Q(status='enrolled') ).update(status='transfered', date_left = timezone.now())
                
#                 # add student to new class 
#                 # add logic here to make it auto or need approval 
#                 StudentClassEnrollment.objects.create(student=student, class_room=to_class, status='active')
#             serializer = StudentDetailSerializer(students,many=True, context = {"request":request})
#             # if serializer.is_valid() :
#             return Response({
#                     "success": f"Student Trasfered to {to_class.name} successfully",
#                     "trans_students": serializer.data
#                 }, status=status.HTTP_200_OK )
                
#         except Exception as e :
#             return Response({"error": "server error"}, status=status.HTTP_200_OK)   
