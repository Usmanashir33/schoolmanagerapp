import os ,random,re
import requests
from decouple import config
from core.c_pegination import CustomPagination   
from django.db.models import Q
from core.permissions import  CheckTransectionPermission


from authUser.serializers import UserSerializer
from notifications.serializers import NotificationSerializer
from notifications.models import Notification
from account.websocketandmail import signal_sender
from account.models import MoneyTransaction
from .serializers import MoneyTransactionSerializer,MiniUserSerializer
from rest_framework.views import APIView

from rest_framework import permissions

from rest_framework import status
from rest_framework.response import Response
from authUser.models import User

FLW_PUBLIC_KEY = config("FLW_PUBLIC_KEY")
FLW_SECRET_KEY = config("FLW_SECRET_KEY")
FLW_SECRET_HASH = config("FLW_SECRET_HASH")

from core.trx_recorders import createWithdrawalStatusChangeTrx,createWithdrawalTrx,createInternalTrx

def identify_field_type(input_value):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'  # Basic email pattern
    phone_regex = r'^\+?\d{10,15}$'  # Matches 10-15 digits, optional '+'
    username_regex = r'^[a-zA-Z0-9_]{3,30}$'  # Alphanumeric and underscores, 3-30 chars

    if re.match(email_regex, input_value):
        user = User.objects.get(email = input_value)
        return user

    elif re.match(phone_regex, input_value):
        user = User.objects.get(phone_number = input_value)
        return user

    elif re.match(username_regex, input_value):
        user = User.objects.get(username = input_value)
        return user
    else:
        return None

class SendMoneyView(APIView):
    permission_classes= [CheckTransectionPermission,]
    def post(self, request):
        try:
            user = request.user
            amount = request.data.get('amount')
            recipient_id = request.data.get('recipient')
            try:
                recipient = User.objects.get(id = recipient_id)
            except:
                return Response({"error":"recipient not found"}, status=status.HTTP_200_OK) 
            
            # user cannot send money to him self
            if str(user.id) == str(recipient_id):
                return Response({"error":"you cannot send money to your self"}, status=status.HTTP_200_OK)
            
            # validate pin here
            pin = request.data.get('payment_pin')
            if user.payment_pin != pin :
                return Response({"error":"wronge pin"}, status=status.HTTP_200_OK)
            
            if user and float(user.account.account_balance) >= float((amount)) :
                # debit and credit here 
                user.account.debit(float(amount)) #user debited
                recipient.account.deposite(float(amount)) #recipient credited
               # send Email and Notification here 
                response = createInternalTrx(request,recipient)
                # print('response: ', response)
                
                if response :
                    return Response({"success":"money sent",'data':response}, status=status.HTTP_200_OK)
            else:
                return Response({"error":"not enough balance"}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server went wrong"}, status=status.HTTP_408_REQUEST_TIMEOUT)
        
class WithdrawalView(APIView):
    permission_classes= [CheckTransectionPermission,]
    def post(self, request):
        try:
            user = request.user
            amount = request.data.get('amount')
            
            # validate pin here
            pin = request.data.get('payment_pin')
            if user.payment_pin != pin :
                return Response({"error":"wronge pin"}, status=status.HTTP_200_OK)
            
            if user and float(user.account.account_balance) >= float((amount)) :
                # debit and credit here 
                user.account.debit(float(amount)) #user debited
                user_data = createWithdrawalTrx(request)
                
                # send Email and Notification here  
                return Response({"success":"success",'resp':user_data}, status=status.HTTP_200_OK)
            else:
                return Response({"success":"not enough balance"}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server went wrong"}, status=status.HTTP_408_REQUEST_TIMEOUT)

class RecentReciepientsView(APIView):
    def get(self, request):
        try:
            user = request.user 
            recepients =User.objects.filter(
                    Q(transfersin__status = 'success',transfersin__user =user ) & 
                    ~Q(transfersin__receiver = user)
                ).order_by("-transfersin__trx_date")
            users =[]
            for 
            data = MiniUserSerializer(recepients,many=True).data
            print("users :" ,data )
            return Response({'success':'success','data':data},status=status.HTTP_200_OK)
        except :
           return Response({"error":"user not found"},status=status.HTTP_200_OK)


