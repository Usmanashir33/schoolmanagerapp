          

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