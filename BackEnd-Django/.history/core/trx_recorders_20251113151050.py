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
from account.serializers import MoneyTransactionSerializer,MiniUserSerializer
from rest_framework.views import APIView

from rest_framework import permissions

from rest_framework import status
from rest_framework.response import Response
from authUser.models import User

FLW_PUBLIC_KEY = config("FLW_PUBLIC_KEY") 
FLW_SECRET_KEY = config("FLW_SECRET_KEY")
FLW_SECRET_HASH = config("FLW_SECRET_HASH")

def createWithdrawalTrx(request,recipient='withdrawal-approval'):
    # send notification and update the user  via websocket
    user = request.user
    amount = request.data.get('amount')
    user_room = f"room{user.id}"
    # recipient_room = f"room{recipient.id}"
    user_data = UserSerializer(user).data
    
    # create trx 
    user_trx = MoneyTransaction.objects.create(
        user = user,
        amount = f"{amount}",
        net_charges = 0.00,
        status = 'pending',
        transaction_type = 'Withdraw',
        notes = request.data.get('note'),
        withdrawal_account_number =  request.data.get('account_number'),    
        withdrawal_account_name = request.data.get('account_name'),
        withdrawal_bank_name = request.data.get('bank_name'),
        withdrawal_bank_code = request.data.get('bank_code'),
        # receiver = recipient
    )
    user_trx.save()
    trx = MoneyTransactionSerializer(user_trx).data
    user_resp = {
        "trx":trx,
        "trx_type":'approval_request',
        "user":user_data
    }
    # send this to approver 
    approver_resp = {
        "type":"send_response",
        "signal_name" : 'approval_request',
        "trx":trx,
    }
    approver = User.objects.get(is_superuser = True)
    approver_room = f"room{approver.id}"
    signal_sender(approver_room,approver_resp) # send trx to approver
    return user_resp

def createWithdrawalStatusChangeTrx(approver,trx,reason,trx_status):
    # send notification and update the user  via websocket
    user = trx.user
    user_room = f"room{user.id}"
    user_data = UserSerializer(user).data
    # create trx 
    trx.status = trx_status
    trx.approver = approver
    trx.save()
    trx_data = MoneyTransactionSerializer(trx).datar
    
    if trx_status == 'cancelled':
        # craete refund trx 
        ref_trx = MoneyTransaction.objects.create(
            user = user,
            amount = f"{trx.amount}",
            net_charges = 0.00,
            status = 'success',
            transaction_type = 'Refund',
        )
        ref_trx.save()
        ref_trx_data = MoneyTransactionSerializer(ref_trx).data
    data = {
        "type":"send_response",
        "signal_name" : 'money_trx',
        'signal_type' : 'refund' if trx_status == 'cancelled' else None ,
        # if this trx is refunding trx itll be treadted otherwise 
        'trx':ref_trx_data if trx_status == 'cancelled' else None,
        "updated_trx":trx_data,
        "user":user_data
    }
    signal_sender(user_room,data) # send trx to the target user
    
    # create notification 
    refund_body = f'Your N{trx.amount} has been refunded. Reason is ({reason})'
    approval_body = f'Your withdrawal request has been approved. Amount: N{trx.amount}'
    notif = Notification.objects.create(
        user = user,
        title = 'Money Refund ' if trx_status == 'cancelled' else 'Withdrawal Approved',
        body =refund_body if trx_status == 'cancelled' else approval_body,
        type = 'success'
    )
    notif.save()
    
    notif = NotificationSerializer(notif).data
    data2 = {
        "type":"send_response",
        "signal_name" : 'money_notif',
        "notif":notif,
        "user":user_data
    }
    signal_sender(user_room,data2) # send notif to target user 
    return trx_data


def createRefundTrx(approver,trx,reason,amount):
    # send notification and update the user  via websocket
    user = trx.user
    user_room = f"room{user.id}"
    user_data = UserSerializer(user).data
    
    # create trx 
    trx.status = 'refunded'
    trx.approver = approver
    trx.save()
    # trx.transaction_type = 'Refund',
    trx_data = MoneyTransactionSerializer(trx).data
    trx.notes = f"{reason} ({trx.notes})" 
    
    data = {
        "type":"send_response",
        "signal_name" : 'money_trx',
        'signal_type' : 'refund'  ,
        # if this trx is refunding trx itll be treadted otherwise 
        'trx': None,
        "updated_trx":trx_data,
        "user":user_data
    }
    signal_sender(user_room,data) # send trx to the target user
    
    # create notification 
    refund_body = f'Your N{amount}  has been refunded. Reason is ({reason})'
    notif = Notification.objects.create(
        user = user,
        title = 'Money Refund ' ,
        body =refund_body,
        type = 'success'
    )
    notif.save()
    
    notif = NotificationSerializer(notif).data
    data2 = {
        "type":"send_response",
        "signal_name" : 'money_notif',
        "notif":notif,
        "user":user_data
    }
    signal_sender(user_room,data2) # send notif to target user 
    return trx_data



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
        sender = user ,
        receiver = recipient
    )
    user_trx.save()
    recipient_trx = MoneyTransaction.objects.create(
        user = recipient,
        amount = f"{amount}",
        net_charges = 0.00,
        status = 'success',
        transaction_type = 'Transfer-In',
        notes = request.data.get('note') ,
        sender = user,
        receiver = recipient
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
        title = 'Money Arrived',
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
def createAirtimeOrDataTrx (request,data):
    # send notification and update the user  via websocket
    user = request.user 
    user_room = f"room{user.id}"
    
    user_data = UserSerializer(user).data
    amount = data.get('amount')
    data = data.get('data')
    status = data.get('status')
    transaction_type = request.data.get('transaction_type')
    
    # create  airtime trx 
    user_trx = MoneyTransaction.objects.create(
        user = user,
        amount = f"{amount}",
        net_charges = 0.00,
        status = status,
        transaction_type = transaction_type, 
    )
    user_trx.save()
    
    
    trx = MoneyTransactionSerializer(user_trx).data
    user_resp = {
        "trx":trx,
        "user":user_data
    }
    signal_sender(recipient_room,data2) # send totic=fication to recipient
    signal_sender(recipient_room,recipient_resp) # send trx to reciepient
    return user_resp 
 