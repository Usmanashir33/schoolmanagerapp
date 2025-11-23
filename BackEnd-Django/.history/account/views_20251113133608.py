import os ,random,re,json
import requests
from decouple import config
from django.shortcuts import render
from django.urls import reverse

from notifications.serializers import NotificationSerializer
from notifications.models import Notification
from .serializers import MoneyTransactionSerializer,WithdrawalAccountSerializer
from .models import AccountNumber,Account,MoneyTransaction,WithdrawalAccount
from core.c_pegination import CustomPagination

from .websocketandmail import signal_sender
from authUser.models import User
from authUser.serializers import UserSerializer

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
FLW_PUBLIC_KEY = config("FLW_PUBLIC_KEY")
FLW_SECRET_KEY = config("FLW_SECRET_KEY")
FLW_SECRET_HASH = config("FLW_SECRET_HASH")
# print('FLW_SECRET_HASH: ', FLW_SECRET_HASH)
def setSuccessText(trx_status):
    if trx_status == 'successful' :
        return 'success'
    elif trx_status == 'pending' :
        return 'pending'
    elif trx_status == 'failed' :
        return 'failed'
    else :
        return 'unknown'
# Create your views here.
def createMoneyTrx (user,data):
    app_fee = data['data']['app_fee']
    MY_FEE = float(0.00)
    total_charges =  float(app_fee) +  MY_FEE
    current_user = User.objects.get(id =user)
    amount = data['data']['amount']
    
    # create trx 
    new_trx = MoneyTransaction.objects.create(
        user = current_user,
        amount = amount,
        net_charges = total_charges,
        trx_id = data['data']['id'],
        trx_ref = data['data']['flw_ref'],
        originator_name = data['meta_data']['originatorname'],
        originator_bank = data['meta_data']['bankname'],
        originator_acc_num = data['meta_data']['originatoraccountnumber'],
        status = setSuccessText(data['data']['status']),
        transaction_type = 'Deposite',
        payment_type = data['data']['payment_type'],
        updated_at = data['data']['created_at'],
        ip_address = data['data']['ip'],
        notes = data['data']['tx_ref'],
    )
    new_trx.save()
    
    # send notification and update the user  via websocket
    user_room = f"room{user}"
    user = UserSerializer(current_user).data
    trx = MoneyTransactionSerializer(new_trx).data
    data = {
        "type":"send_response",
        "signal_name" : 'money_trx',
        "trx":trx,
        "user":user
    }
    
    notif = Notification.objects.create(
        user = current_user,
        title = 'Deposite Confirmed',
        body =f'Your Deposite of N{amount} has been received',
        type = 'success'
    )
    notif.save()
    notif = NotificationSerializer(notif).data
    data2 = {
        "type":"send_response",
        "signal_name" : 'money_notif',
        "notif":notif,
        "user":user
    }
    
    signal_sender(user_room,data)
    signal_sender(user_room,data2)
    # send Email here 

def depositeConfirmed (respData) :
    data = respData['data']
    sender_id = data['tx_ref'].split('seller-')[1]
    trx_id = data['id']
    amount_sent = data['charged_amount']
    app_fee = data['app_fee']
    MY_FEE = float(0.00)
    amount_to_be_added = float(amount_sent) - float(app_fee) - MY_FEE
    
    try :
        sender_account = Account.objects.get(user = sender_id)
        transection_exists = MoneyTransaction.objects.filter(trx_id = trx_id).exists()
    except :
        return None
    
    if sender_account and not transection_exists:
        # add money received and create transection record 
        sender_account.deposite(amount_to_be_added)
        sender_account.save()
        
        # create transection record 
        new_trx = createMoneyTrx(sender_id,respData)
    else :
        print("transection found already ")
        
class AccountNumberCreationView(APIView):
    print("creating Account number")
    def post(self, request):
        url = "https://api.flutterwave.com/v3/virtual-account-numbers"
        user = request.user
        if user.account.accountnumbers.all():
            return Response({'success':'max accounts exit for the user'},status=status.HTTP_200_OK)
        print("accounts creating..... ")
        try :
            payload = {
                "email":user.email ,
                "is_permanent": True,  # Set to true for a permanent account
                "bvn": "22583653416",  # Optional but recommended
                "tx_ref": f"seller-{user.id}",
                'amount' : '10000',
                "firstname": user.username,
                "lastname":f"{user.first_name}-{user.last_name}",
                "phonenumber": user.phone_number,
                "narration": f"seller-{user.username}",
                "currency": "NGN"  # Nigerian Naira
            }
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {FLW_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            response = requests.post(url, json=payload, headers=headers)
            response = json.loads(response.text)
            if response['status'] == 'success' and response['message'] == "Virtual account created" :
               data = response['data']
               new_account_num = AccountNumber.objects.create(
                    account = user.account,
                    account_number = data['account_number'],
                    flw_ref = data['flw_ref'],
                    bank_name = data['bank_name'].split(' ')[0] ,
                    date_created = data['created_at']
               )
               user.account.account_balance + int(data['amount'])  # to avoid making balance zero when the new accont created
               user.save()
               
            return Response({'success':'account number craeted'},status=status.HTTP_200_OK)
        except :
            return Response({'error':'server failed '},status=status.HTTP_200_OK)

class FlutterWebHookView(APIView):
    def post(self, request, *args, **kwargs):
        secretHash = FLW_SECRET_HASH
        signature = request.headers.get("verif-hash")
        
        if not signature or signature != secretHash :
            # This response is not from my Flutterwave; discard it
            print('response: ', 'not flutterwave')
            # return Response({'error':'server failed '},status=status.HTTP_200_OK)
        
        response = request.data
        if response.get('event') == 'charge.completed' :
            depositeConfirmed(response)
        return Response({'success':'success'}, status=status.HTTP_200_OK)

            
    def get(self, request, *args, **kwargs):
        pass
    
class TransectionsView(APIView):
    def get(self, request, *args, **kwargs):
        paginator = CustomPagination()
        # try :
            user = request.user
            money_trxs = MoneyTransaction.objects.filter(user = user.id).order_by('-trx_date')
            paginated_trxs = paginator.paginate_queryset(money_trxs,request)
            money_trxs = MoneyTransactionSerializer(paginated_trxs,many=True).data
            money_trxs = paginator.get_paginated_response(money_trxs)
            return Response({'data':money_trxs.data,'name':'transections'},status=status.HTTP_200_OK)
        # except :
            # return Response({'error':'server failed '},status=status.HTTP_200_OK)
class TransectionView(APIView):
    def get(self, request, trx_id,*args, **kwargs):
        try :
            try:
                trxs = MoneyTransaction.objects.get(id=trx_id)
            except:
                pass
            if not trxs :
                return Response({'error':'trx not found'},status=status.HTTP_200_OK)
            money_trxs = MoneyTransactionSerializer(trxs,).data
            return Response({'success':'success','data':money_trxs},status=status.HTTP_200_OK)
        except :
            return Response({'error':'server failed '},status=status.HTTP_200_OK)

class NotificationsView(APIView):
    def get(self, request, *args, **kwargs):
        paginator = CustomPagination()
        try :
            user = request.user
            money_notif = Notification.objects.filter(user = user.id).order_by('-date')
            
            paginated_notif = paginator.paginate_queryset(money_notif,request)
            money_notif = NotificationSerializer(paginated_notif,many=True).data
            money_notif = paginator.get_paginated_response(money_notif)
            return Response({'data':money_notif.data['results'],'name':'notifications'},status=status.HTTP_200_OK)
        except :
            return Response({'error':'server failed '},status=status.HTTP_200_OK)

class ReadNotificationsView(APIView):
    def get(self, request,*args, **kwargs):
        try :
            user = request.user
            unread_notif = Notification.objects.filter(user = user.id,viewed = False)
            for notif in unread_notif :
                notif.viewed = True
                notif.save()
            return Response({'name':'notif_read'},status=status.HTTP_200_OK)
        except :
            return Response({'error':'server failed '},status=status.HTTP_200_OK)

class DeleteNotificationsView(APIView):
    def get(self, request ):
        try :
            user = request.user
            notifs = Notification.objects.filter(user = user.id,)
            for notif in notifs :
                # notif.delete()
                pass
            return Response({'name':'notif_delete_all'}, status = status.HTTP_200_OK)
        except :
            return Response({'error':'server failed '}, status = status.HTTP_200_OK)
    
    def delete(self, request, notif_id):
        try :
            user = request.user
            notif = Notification.objects.get(id = notif_id)
            notif.delete()
            return Response({'name':'notif_delete',"id":notif_id},status=status.HTTP_200_OK)
        except :
            return Response({'error':'server failed '},status=status.HTTP_200_OK)
        
class SettingWithDrawalAccount(APIView):
    def __init__(self, **kwargs):
        self.nigerian_accounts_url = "https://api.flutterwave.com/v3/banks/NG"
        self.account_resulve_url = "https://api.flutterwave.com/v3/accounts/resolve"
        
        self.headData = {
        "accept": "application/json",
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
        "Content-Type": "application/json"
        }
        super().__init__(**kwargs)
    
    def post(self, request ):
        try :
            user = request.user
            action = request.data.get('action')
            if action == 'fetchBanks':
                banks = requests.get(self.nigerian_accounts_url, headers= self.headData).text
                return Response({'banks':banks}, status = status.HTTP_200_OK)
            if action == 'verifyBank':
                payload = {
                    "account_number": request.data.get("account_number"),
                    "account_bank": request.data.get("bank_code")
                }
                account_fetched = requests.post(self.account_resulve_url, json=payload, headers=self.headData).text
                return Response({'account_fetched':account_fetched}, status = status.HTTP_200_OK)
            if action == 'saveBank':
                payment_pin = request.data.get('payment_pin')
                
                # validate pin
                if payment_pin != user.payment_pin:
                    print(' invalid pin ')
                    return Response({'error':'invalid pin'}, status = status.HTTP_200_OK)
                
                # validate account existance 
                account_found = user.account.withdrawalaccounts.filter(
                    account_number = request.data.get("account_number"),
                    bank_code = request.data.get("bank_code") 
                ).exists()
                
                if account_found:
                    print(' accound found ')
                     
                    return Response({'error':'account already exist'}, status = status.HTTP_200_OK)
                
                # validate account name
                new_account = WithdrawalAccount.objects.create(
                    account = user.account,
                    account_number =  request.data.get("account_number"),
                    account_name =  request.data.get("account_name"),
                    bank_name =  request.data.get("bank_name"),
                    bank_code =  request.data.get("bank_code")
                )
                is_default = request.data.get('is_default',False)
                if is_default :
                    # set it default
                    for acc in user.account.withdrawalaccounts.all() :
                        acc.is_default = False
                        acc.save()
                    new_account.is_default = True
                    new_account.save()
                new_account = WithdrawalAccountSerializer(new_account).data
                return Response({'success':'New Account Added','new_account':new_account}, status = status.HTTP_200_OK)
        except :
            return Response({'error':'server failed '}, status = status.HTTP_200_OK)
def identify_trx(search) :
    try :
        money_trxs = MoneyTransaction.objects.filter(id = search)
        if money_trxs :
            return money_trxs
        money_trxs = MoneyTransaction.objects.filter(api_trx_id = search)
        if money_trxs :
            return money_trxs
        money_trxs = MoneyTransaction.objects.filter(api_trx_ref = search)
        if money_trxs :
            return money_trxs
        # not available 
        return None
    except :
        return None
        
class SearchTrxView(APIView) :
    def post(self, request):
        try:
            search = request.data.get('search')
            money_trxs = identify_trx(search)
            if money_trxs :
                money_trxs = MoneyTransactionSerializer(money_trxs,many=True).data
                return Response(money_trxs,status=status.HTTP_200_OK)
            else :
                return Response({"error":"transection not found!"}, status=status.HTTP_200_OK)
        except :
           return Response({"error":"server failed"},status=status.HTTP_200_OK)
       
class FetchWithdrawalAccount(APIView): 
    def get(self, request ):
        try :
            user = request.user
            accounts = user.account.withdrawalaccounts.all()
            accounts = WithdrawalAccountSerializer(accounts,many=True).data
            return Response({'accounts':accounts}, status = status.HTTP_200_OK)
        except :
            return Response({'error':'server failed '}, status = status.HTTP_200_OK)
class EditWithdrawalAccount(APIView):
    def delete(self, request, account_id ):
        try :
            user = request.user
            payment_pin = request.data.get('payment_pin')
            # validate pin
            if payment_pin != user.payment_pin:
                return Response({'error':'invalid pin'}, status = status.HTTP_200_OK)
            account = WithdrawalAccount.objects.get(id = account_id)
            if account.account == user.account:
                account.delete()
                return Response({'success':'account deleted','id':account_id}, status = status.HTTP_200_OK)
            return Response({'error':'account not found'}, status = status.HTTP_200_OK)
        except :
            return Response({'error':'server failed '}, status = status.HTTP_200_OK)
    def put(self, request, account_id ):
        try :
            user = request.user
            payment_pin = request.data.get('payment_pin')
            # validate pin
            if payment_pin != user.payment_pin:
                return Response({'error':'invalid pin'}, status = status.HTTP_200_OK)
            account = WithdrawalAccount.objects.get(id = account_id)
            if account.account == user.account:
                # remove remaining_defaults 
                for acc in user.account.withdrawalaccounts.all() :
                    acc.is_default = False
                    acc.save()
                # set_it default
                account.is_default = True
                account.save()
                return Response({'success':'account is set to default ','id':account_id,'defaulting':True}, status = status.HTTP_200_OK)
            return Response({'error':'account not found'}, status = status.HTTP_200_OK)
        except :
            return Response({'error':'server failed '}, status = status.HTTP_200_OK)