from urllib import response
from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.db.models import Sum
from django.utils.timezone import localtime
from django.db.models import Sum, Avg
import random

from datetime import timedelta
from django.utils import timezone
from core.permissions import CheckStaffPermission
from .serializers import UsersSerializer
from authUser.serializers import UserSerializer
from core.c_pegination import UsersCustomPagination
from account.models import MoneyTransaction
from account.models import Account
from account.serializers import MoneyTransactionSerializer
from decouple import config
from core.trx_recorders import createWithdrawalStatusChangeTrx,createRefundTrx,createInternalTrx
from core.emails.email_templates.emails import generate_otp_email,generate_login_email,generate_registration_email
from core.emails.utils.email_service import send_html_email

def generate_verification_code() :
    code = random.randint(12345,98769)
    return  code 

from core.c_pegination import CustomPagination  
FLW_PUBLIC_KEY = config("FLW_PUBLIC_KEY")
FLW_SECRET_KEY = config("FLW_SECRET_KEY")
FLW_SECRET_HASH = config("FLW_SECRET_HASH")

User = get_user_model()

class StaffUsersDashboardView(APIView):
    permission_classes = [CheckStaffPermission,]

    def get(self, request):
        paginator = UsersCustomPagination()
        # Define time range for "new users" — last 7 days
        one_week_ago = timezone.now() - timedelta(days=7)

        total_users = User.objects.all().count()
        new_users = User.objects.filter(date_joined__gte=one_week_ago).count()
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = User.objects.filter(is_active=False).count()
        users = User.objects.all()
        paginated_users = paginator.paginate_queryset(users,request)
        users_data = UsersSerializer(paginated_users,many=True).data
        paginated_users_resp = paginator.get_paginated_response(users_data).data

        return Response({
            "users" :paginated_users_resp,
            "total_users" : total_users,
            "new_users" : new_users,
            "active_users" : active_users,
            "inactive_users" : inactive_users,
        })

class StaffTrxsDashboardView(APIView):
    permission_classes = [CheckStaffPermission,]

    def get(self, request):
        paginator = UsersCustomPagination()
        # Define time range for "new users" — last 7 days
        one_week_ago = timezone.now() - timedelta(days=7)

        
        recent_trx = MoneyTransaction.objects.filter(trx_date__gte=one_week_ago).count()
        credit_trxs =['Deposite',]
        debit_trxs =['Transfer-Out','Withdraw']
        trx_status =['success','approved']
        
        recent_credit_sum = MoneyTransaction.objects.filter(
            status__in = trx_status
        ).filter(
            transaction_type__in=credit_trxs
        ).filter(
            trx_date__gte=one_week_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        recent_debit_sum = MoneyTransaction.objects.filter(
            status__in = trx_status
        ).filter(
            transaction_type__in=debit_trxs
        ).filter(
            trx_date__gte=one_week_ago
        ).aggregate(total=Sum('amount'))['total'] or 0

        
        # results data 
        trxs = MoneyTransaction.objects.all()
        paginated_trxs = paginator.paginate_queryset(trxs,request)
        trxs_data = MoneyTransactionSerializer(paginated_trxs,many=True).data
        paginated_trxs_resp = paginator.get_paginated_response(trxs_data).data

        return Response({
            "trxs" :paginated_trxs_resp,
            "recent_credit_sum" : recent_credit_sum,
            "recent_debit_sum" : recent_debit_sum,
            "recent_trx" : recent_trx,
        })


class StaffUserDetailView(APIView):
        permission_classes = [CheckStaffPermission,]

        def get_user(self, id):
            print('id: ', id)
            try:
                return User.objects.get(id=id)
            except User.DoesNotExist:
                return None

        def get(self, request, user_id):
            try :
                
                user = self.get_user(user_id)
                if user is None:
                    return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
                
                serializer = UserSerializer(user)
                return Response(serializer.data,status=status.HTTP_200_OK)
            except :
                return Response({"error":'server went Wronge!'},status=status.HTTP_200_OK)

        def put(self, request, user_id):
            try :
                user = request.user 
                pins = request.data.get('staff_pins')
                if hasattr(user, 'staffpins'):
                    pin = user.staffpins.pins
                else:
                    # handle missing pin
                    pin = None
                if not pin or not pins == pin :
                    return Response({'error': 'wronge pins.'}, status=status.HTTP_200_OK)

                user = self.get_user(user_id)
                if user is None:
                    return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

                # get addministrative acts  
                email_varified = request.data['emailVerified']
                is_active = request.data.get('accountActive')
                kyc_confirmed = request.data.get('kycConfirmed')
                can_transect = request.data['canTransact']
                is_staff = request.data['staffAccess']
                log_with_otp = request.data['otpLogin']
                attrs1 = ['is_active','email_varified','kyc_confirmed','can_transect','is_staff','log_with_otp']
                update1 = [is_active,email_varified,kyc_confirmed,can_transect,is_staff,log_with_otp]
                
                for index,update in enumerate(update1) : #loop through updates to change the change
                    if hasattr(user,attrs1[index]) :
                        setattr(user, attrs1[index], update)
                        user.save()
                serializer = UserSerializer(user)
                return Response(serializer.data,status=status.HTTP_200_OK)
            except :
                return Response({"error":'server went Wronge!'},status=status.HTTP_200_OK)

class StaffTrxDetailView(APIView):
        permission_classes = [CheckStaffPermission,]

        def get_trx(self, id):
            try:
                return MoneyTransaction.objects.get(id=id)
            except MoneyTransaction.DoesNotExist:
                return None

        def get(self, request, trx_id):
            try :
                
                trx = self.get_trx(trx_id)
                if trx is None:
                    return Response({'error': 'Trx not found.'}, status=status.HTTP_404_NOT_FOUND)
                
                serializer = MoneyTransactionSerializer(trx)
                return Response(serializer.data,status=status.HTTP_200_OK)
            except :
                return Response({"error":'server went Wronge!'},status=status.HTTP_200_OK)

        def put(self, request, trx_id):
            # refunding the perticuler trx 
            try :
                refund_note = request.data.get('refund_note')
                refund_reason = request.data.get('refund_reason')
                reason = f"{refund_reason}: {refund_note}"
                refund_amount = request.data.get('refund_amount')
                user = request.user 
                pins = request.data.get('staff_pins')
                
                if hasattr(user, 'staffpins'):
                    pin = user.staffpins.pins
                else:
                    # handle missing pin
                    pin = None
                if not pin or not pins == pin :
                    return Response({'error': 'wronge pins.'}, status=status.HTTP_200_OK)

                trx = self.get_trx(trx_id)
                if trx is None:
                    return Response({'error': 'Trx not found.'}, status=status.HTTP_404_NOT_FOUND)
                total_amount = float(refund_amount)
                if trx.status == 'refunded':
                    return Response({'error': 'refund not allowed'}, status=status.HTTP_404_NOT_FOUND)
                    
                if float(refund_amount) > float(trx.amount) + float(trx.net_charges) :
                    return Response({'error': 'refund amount exceeded'}, status=status.HTTP_404_NOT_FOUND)

                # start the logic here 
                # refund 
                # create refund trx here and notify user 
                trx.user.account.deposite(float(trx.amount))
                
                refunded_trx =  createRefundTrx(user,trx,reason,total_amount)
                return Response({"success":"cancelled",'data':refunded_trx}, status=status.HTTP_200_OK)
            except :
                return Response({"error":'server went Wronge!'},status=status.HTTP_200_OK)
    
class WithdrawalRequestView(APIView):
    permission_classes = [CheckStaffPermission,]
    def get(self, request):
        paginator = CustomPagination()
        try:
            # pending_withdrawals = MoneyTransaction.objects.filter(transaction_type = 'Withdraw',status = 'pending')
            pending_withdrawals = MoneyTransaction.objects.filter(transaction_type = 'Withdraw')
            paginated_data = paginator.paginate_queryset(pending_withdrawals,request)
            pending_withdrawals = MoneyTransactionSerializer(paginated_data,many=True).data
            pending_withdrawals = paginator.get_paginated_response(pending_withdrawals)
            return Response({'data':pending_withdrawals.data['results']}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server went wrong"}, status=status.HTTP_408_REQUEST_TIMEOUT)
        
    def post(self, request,):
        try:
            user = request.user
            trx_id = request.data.get('trx_id')
            approval = request.data.get('approval')
            pins = request.data.get('staff_pins')

            try :
                trx = MoneyTransaction.objects.get(id = trx_id)
            except :
                return Response({"error":"trx is not found"}, status=status.HTTP_200_OK)
            
            # validate pin here
            if hasattr(user, 'staffpins'):
                pin = user.staffpins.pins
            else:
                # handle missing pin
                pin = None
            if not pin or not pins == pin :
                    return Response({'error': 'wronge pins.'}, status=status.HTTP_200_OK)

    
            # only admin can approve trx
            # if user.is_superuser == False:
            #     return Response({"error":"you are not allowed to process this trx"}, status=status.HTTP_200_OK)
            
            # check if transection already approved
            if not trx.status == 'pending':
                return Response({"error":"this trx is already processed"}, status=status.HTTP_200_OK)
                 
 
            if approval == 'approve': # the withdrawal is approved
                # configure flutter wave here 
                url = "https://api.flutterwave.com/v3/transfers"
                payload = {
                    "account_bank": f"{trx.withdrawal_bank_code}",
                    "account_number": f"{trx.withdrawal_account_number}",
                    "amount": int(trx.amount),
                    "currency": f"NGN",
                    "beneficiary_name": f"{trx.withdrawal_account_name}",
                    "debit_currency": f"NGN",
                    "reference": f"{trx.id}",
                    # "callback_url": f"https://webhook.site/5f9a659a-11a2-4925-89cf-8a59ea6a019a",
                    "narration": f"withdrawal from {trx.user.username}",
                }
                headers = {
                    "accept": "application/json",
                    "Authorization": f"Bearer {FLW_SECRET_KEY}",
                    "Content-Type": "application/json"
                }
                # response = requests.post(url, json=payload, headers=headers)
                # print('response: ', response.text)
                print(approval)
                reason = request.data.get('reason')
                approved_trx =  createWithdrawalStatusChangeTrx(user,trx,reason,'approved')
                return Response({"success":"approved",'data':approved_trx}, status=status.HTTP_200_OK)
             
                
            elif approval == 'reject' or approval == 'cancel' :
                # initiate refund here and send notification to the user with transection
                # create refund trx here and notify user 
                trx.user.account.deposite(float(trx.amount))
                reason = request.data.get('reason')
                cancelled_trx =  createWithdrawalStatusChangeTrx(user,trx,reason,'cancelled')
                return Response({"success":"cancelled",'data':cancelled_trx}, status=status.HTTP_200_OK)
            
            elif approval == 'cancel' : # approval == 'cancel' 
                # initiate refund here and send notification to the user with transection
                # create refund trx here and notify user 
                trx.user.account.deposite(float(trx.amount))
                reason = request.data.get('reason')
                cancelled_trx =  createWithdrawalStatusChangeTrx(user,trx,reason,'cancelled')
                return Response({"success":"cancelled",'data':cancelled_trx}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server went wrong"}, status=status.HTTP_408_REQUEST_TIMEOUT)
        

def percent_change(current, previous):
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 1)

class AnalysisRequestView(APIView):
    permission_classes = [CheckStaffPermission,]
    def post (elf, request):
        # Define time ranges
        try :
            # Get the period from request data
            period = request.data.get('period', 'daily').lower()  # 'daily', 'weekly', 'monthly'

            today = localtime().date()
            yesterday = today - timedelta(days=1)
            start_of_month = today.replace(day=1)
            start_of_week = today - timedelta(days=today.weekday())
            last_week = start_of_week - timedelta(days=7)
            last_month_start = (start_of_month - timedelta(days=1)).replace(day=1)


            # Total Balance
            total_balance = Account.objects.aggregate(total=Sum('account_balance'))['total'] or 0

            # Transaction type helpers
            INFLOW_TYPES = ['Deposite',]
            OUTFLOW_TYPES = ['Withdraw',]
            
            # === DAILY ===
            if period == 'daily':
                daily_inflow = MoneyTransaction.objects.filter(
                    transaction_type__in=INFLOW_TYPES, trx_date__date=today
                ).aggregate(total=Sum('amount'))['total'] or 0

                yesterday_inflow = MoneyTransaction.objects.filter(
                    transaction_type__in=INFLOW_TYPES, trx_date__date=yesterday
                ).aggregate(total=Sum('amount'))['total'] or 0

                daily_outflow = MoneyTransaction.objects.filter(
                    transaction_type__in=OUTFLOW_TYPES, trx_date__date=today
                ).aggregate(total=Sum('amount'))['total'] or 0

                yesterday_outflow = MoneyTransaction.objects.filter(
                    transaction_type__in=OUTFLOW_TYPES, trx_date__date=yesterday
                ).aggregate(total=Sum('amount'))['total'] or 0

                daily_transactions = MoneyTransaction.objects.filter( trx_date__date=today)
                yesterday_transactions = MoneyTransaction.objects.filter( trx_date__date=yesterday)
                daily_avg = daily_transactions.aggregate(avg=Avg('amount'))['avg'] or 0
                yesterday_avg = yesterday_transactions.aggregate(avg=Avg('amount'))['avg'] or 0
                # === Daily REVENUE ===
                revenue = MoneyTransaction.objects.filter(
                    transaction_type__in=INFLOW_TYPES, trx_date__date=today
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                #prepare daily response 
                daily_data = {
                    "summary": {
                        "total_balance": {
                            "value": float(total_balance),
                            "change": "0.0%"  # You can calculate profit percent if applicable
                        },
                        "revenue": {
                            "value": float(revenue),
                            "change": f"{percent_change(revenue, 0)}%"  # No prev day tracking yet
                        }
                    },
                    "analysis": {
                        "inflow": {
                            "value": float(daily_inflow),
                            "change": f"{percent_change(daily_inflow, yesterday_inflow)}%"
                        },
                        "outflow": {
                            "value": float(daily_outflow),
                            "change": f"{percent_change(daily_outflow, yesterday_outflow)}%"
                        },
                        "total_transactions": {
                            "value": daily_transactions.count(),
                            "change": f"{percent_change(daily_transactions.count(), yesterday_transactions.count())}%"
                        },
                        "average_value": {
                            "value": float(daily_avg),
                            "change": f"{percent_change(daily_avg, yesterday_avg)}%"
                        }
                    }
                }
                return Response(daily_data, status=status.HTTP_200_OK)
            
            # === WEEKLY ===
            if period == 'weekly':
                weekly_inflow = MoneyTransaction.objects.filter(
                    transaction_type__in=INFLOW_TYPES, trx_date__date__gte=start_of_week
                ).aggregate(total=Sum('amount'))['total'] or 0

                last_week_inflow = MoneyTransaction.objects.filter(
                    transaction_type__in=INFLOW_TYPES, trx_date__date__gte=last_week
                ).aggregate(total=Sum('amount'))['total'] or 0

                weekly_outflow = MoneyTransaction.objects.filter(
                    transaction_type__in=OUTFLOW_TYPES, trx_date__date__gte=start_of_week
                ).aggregate(total=Sum('amount'))['total'] or 0

                last_week_outflow = MoneyTransaction.objects.filter(
                    transaction_type__in=OUTFLOW_TYPES, trx_date__date__gte=last_week
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                weekly_transactions = MoneyTransaction.objects.filter(trx_date__date__gte=start_of_week)
                last_week_transactions = MoneyTransaction.objects.filter(trx_date__date__gte=last_week)
                weekly_avg = weekly_transactions.aggregate(avg=Avg('amount'))['avg'] or 0
                last_week_avg = last_week_transactions.aggregate(avg=Avg('amount'))['avg'] or 0
                # weekly reven ue
                revenue = MoneyTransaction.objects.filter(
                    transaction_type__in=INFLOW_TYPES, trx_date__date__gte=start_of_week
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                # prepare weekly response
                weekly_data = {
                    "summary": {
                        "total_balance": {
                            "value": float(total_balance),
                            "change": "0.0%"  # You can calculate profit percent if applicable
                        },
                        "revenue": {
                            "value": float(revenue),
                            "change": f"{percent_change(revenue, 0)}%"  # No prev week tracking yet
                        }
                    },
                    "analysis": {
                        "inflow": {
                            "value": float(weekly_inflow),
                            "change": f"{percent_change(weekly_inflow, last_week_inflow)}%"
                        },
                        "outflow": {
                            "value": float(weekly_outflow),
                            "change": f"{percent_change(weekly_outflow, last_week_outflow)}%"
                        },
                        "total_transactions": {
                            "value": weekly_transactions.count(),
                            "change": f"{percent_change(weekly_transactions.count(), last_week_transactions.count())}%"
                        },
                        "average_value": {
                            "value": float(weekly_avg),
                            "change": f"{percent_change(weekly_avg, last_week_avg)}%"
                        }
                    }
                }
                return Response(weekly_data, status=status.HTTP_200_OK)
            
            if period == 'monthly':
                # === MONTHLY ===
                monthly_inflow = MoneyTransaction.objects.filter(
                    transaction_type__in=INFLOW_TYPES, trx_date__date__gte=start_of_month
                ).aggregate(total=Sum('amount'))['total'] or 0
                last_month_inflow = MoneyTransaction.objects.filter(
                    transaction_type__in=INFLOW_TYPES, trx_date__date__gte=last_month_start
                ).aggregate(total=Sum('amount'))['total'] or 0
                monthly_outflow = MoneyTransaction.objects.filter(
                    transaction_type__in=OUTFLOW_TYPES, trx_date__date__gte=start_of_month
                ).aggregate(total=Sum('amount'))['total'] or 0
                last_month_outflow = MoneyTransaction.objects.filter(
                    transaction_type__in=OUTFLOW_TYPES, trx_date__date__gte=last_month_start
                ).aggregate(total=Sum('amount'))['total'] or 0
                monthly_transactions = MoneyTransaction.objects.filter(trx_date__date__gte=start_of_month)
                last_month_transactions = MoneyTransaction.objects.filter(trx_date__date__gte=last_month_start)
                monthly_avg = monthly_transactions.aggregate(avg=Avg('amount'))['avg'] or 0
                last_month_avg = last_month_transactions.aggregate(avg=Avg('amount'))['avg'] or 0

                # === MONTHLY REVENUE ===
                revenue = MoneyTransaction.objects.filter(
                    transaction_type__in=INFLOW_TYPES, trx_date__date__gte=start_of_month
                ).aggregate(total=Sum('amount'))['total'] or 0

                # === ACTIVE INVESTMENTS (example: number of successful transfers-out) ===
                active_investments = MoneyTransaction.objects.filter(
                    transaction_type='Transfer-Out', status='success'
                ).count()
                
                # prepare monthly response
                
                monthly_data = {
                    "summary": {
                        "total_balance": {
                            "value": float(total_balance),
                            "change": "0.0%"  # You can calculate profit percent if applicable
                        },
                        "revenue": {
                            "value": float(revenue),
                            "change": f"{percent_change(revenue, 0)}%"  # No prev month tracking yet
                        },
                        "active_investments": active_investments
                    },
                    "analysis": {
                        "inflow": {
                            "value": float(monthly_inflow),
                            "change": f"{percent_change(monthly_inflow, last_month_inflow)}%"
                        },
                        "outflow": {
                            "value": float(monthly_outflow),
                            "change": f"{percent_change(monthly_outflow, last_month_outflow)}%"
                        },
                        "total_transactions": {
                            "value": monthly_transactions.count(),
                            "change": f"{percent_change(monthly_transactions.count(), last_month_transactions.count())}%"
                        },
                        "average_value": {
                            "value": float(monthly_avg),
                            "change": f"{percent_change(monthly_avg, last_month_avg)}%"
                        }
                    }
                }
                return Response(monthly_data, status=status.HTTP_200_OK)
            return Response({"error": "Invalid period specified"}, status=status.HTTP_400_BAD_REQUEST)
    
        except Exception as e:
            print(f"Error in AnalysisRequestView: {e}")
            return Response({"error": "server"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class StaffPinUpdateView(APIView):
    permission_classes = [CheckStaffPermission,]
    def post(self, request):
        try:
            user = request.user
            requst_type = request.data.get('requst_type')
            staff_pin = request.data.get('staff_pin')
            staff_otp = request.data.get('staff_otp')
            
            if  requst_type == 'request':
                # send Email here with otp 
                    email_verification_code = generate_verification_code() 
                    user. email_verification_code =  email_verification_code 
                    user.save()
                    # send email here 
                    print('Email V/C:',email_verification_code)
                    try:
                        html_content = generate_otp_email(user.username,email_verification_code)
                        send_html_email.delay(
                            subject="🔐 Your Fentech OTP Code",
                            to_email=user.email,
                            html_content=html_content
                        )
                    except :
                        pass
                    return Response({'success': 'otp_sent'}, status=status.HTTP_200_OK)

            else : #updating the staff pin 
                if not user. email_verification_code == staff_otp :
                    # for securoty recycle the otp 
                    email_verification_code = generate_verification_code() 
                    user.email_verification_code =  email_verification_code 
                    user.save()
                    return Response({'error': 'invalid OTP.'}, status=status.HTTP_200_OK)
                    
                    
                if hasattr(user, 'staffpins'):
                    user.staffpins.pins = staff_pin
                    user.staffpins.save()
            
                return Response({'success': 'pins updated successfully.'}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server went wrong"}, status=status.HTTP_408_REQUEST_TIMEOUT) 