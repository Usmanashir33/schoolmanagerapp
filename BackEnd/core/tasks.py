from celery import shared_task
import requests
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

class TermiiSMSService:
    BASE_URL = "https://v3.api.termii.com/api"
    @staticmethod
    def send_sms(phone, message):
        try:

            url = f"{TermiiSMSService.BASE_URL}/sms/send " 

            payload = {
                "api_key": settings.TERMII_API_KEY,
                "to": phone,
                "from": settings.TERMII_SENDER_ID,
                "sms": message,
                "type": "plain",
                "channel": "generic",
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()

            return {
                "success": True,
                "data": response.json()
            }

        except requests.exceptions.RequestException as e:

            return {
                "success": False,
                "error": str(e)
            }
            
@shared_task(bind=True, max_retries=3)
def send_ordinary_sms(self, phone:str ,message:str) :
    try:
        result = TermiiSMSService.send_sms(phone,message)
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)

@shared_task(bind=True, max_retries=2)
def send_html_email(self, subject: str, to_email , html_content: str, text_content: str = "View this email in HTML format."):
    print("EMAIL TASK STARTED")
    # send email logic
    try:
        # make it for to_email to be list if not isinstance(to_email, list):
        if not isinstance(to_email, list):
            to_email = [to_email]
            
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_email,
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        print("EMAIL SENT SUCCESS")
        
    except Exception as e:
        print("EMAIL FAILED:", str(e))
        raise self.retry(exc=e, countdown=10)
    

