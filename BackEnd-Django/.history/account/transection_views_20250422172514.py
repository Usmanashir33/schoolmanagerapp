import os ,random,re
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import get_object_or_404
from . import serializers

from a.serializers import UserSerializer
from notifications.serializers import NotificationSerializer
from notifications.models import Notification
from account.websocketandmail import signal_sender
from account.models import MoneyTransaction
from account.serializers import MoneyTransactionSerializer
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from .models import User , KYC
from .serializers import           


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

def createInternalTrx (request,recipient):
    # send notification and update the user  via websocket
    user = request.user
    amount = request.data.get('amount')
    user_room = f"room{user.id}"
    recipient_room = f"room{recipient.id}"
    
    user_data = UserSerializer(user).data
    recipient_data = UserSerializer(recipient).data
    # create trx 
    user_trx = MoneyTransaction.objects.create(
        user = user,
        amount = f"{amount}",
        net_charges = 0.00,
        status = 'success',
        transaction_type = 'Transfer-Out',
        notes = request.data.get('note'),
        receiver = recipient
    )
    user_trx.save()
    recipient_trx = MoneyTransaction.objects.create(
        user = recipient,
        amount = f"{amount}",
        net_charges = 0.00,
        status = 'success',
        transaction_type = 'Transfer-In',
        notes = request.data.get('note')
    )
    recipient_trx.save()
    
    trx = MoneyTransactionSerializer(user_trx).data
    user_resp = {
        "trx":trx,
        "user":user_data
    }
    # for recipient responses 
    trx = MoneyTransactionSerializer(recipient_trx).data
    recipient_resp = {
        "type":"send_response",
        "signal_name" : 'money_trx',
        "trx":trx,
        "user":recipient_data
    }
    
    recipient_notif = Notification.objects.create(
        user = recipient,
        title = 'Internal Transfer Comfirmed',
        body =f'{user.username} has sent you {amount}',
        type = 'success'
    )
    recipient_notif.save()
    recipient_notif = NotificationSerializer(recipient_notif).data
    
    data2 = {
        "type":"send_response",
        "signal_name" : 'money_notif',
        "notif":recipient_notif,
        "user":user_data
    }
    signal_sender(recipient_room,data2) # send totic=fication to recipient
    signal_sender(recipient_room,recipient_resp) # send trx to reciepient
    return user_resp
 
class SendMoneyView(APIView):
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
                if response :
                    return Response({"success":"money sent",'data':response}, status=status.HTTP_200_OK)
            else:
                return Response({"error":"not enough balance"}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server went wrong"}, status=status.HTTP_408_REQUEST_TIMEOUT)