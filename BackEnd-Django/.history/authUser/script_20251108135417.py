# print("Hello, World!")
from django.contrib.auth.hashers import make_password, check_password

from.models import User
users = User.objects.all()
for user in users:
    if user.payment_pin:
        user.payment_pin = make_password(user.payment_pin)
        user.save()
        print(f"Updated payment pin for user: {user.email}")
    else:
        print(f"No payment pin set for user: {user.email}")