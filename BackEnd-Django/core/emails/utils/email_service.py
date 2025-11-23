from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from celery import shared_task

@shared_task # to call the redis attention 
def send_html_email(subject: str, to_email: str, html_content: str, text_content: str = "View this email in HTML format."):
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    

