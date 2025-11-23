import os
import sys
import django

# Add backproject root (where manage.py lives) to Python path
sys.path.append(r"C:\Users\Welcome Sir\Desktop\backend backproject\backend back")

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backproj.settings")

# Setup Django
django.setup()

# print("Hello, World!")
from django.contrib.auth.hashers import make_password, check_password

from authUser.models import User
users = User.objects.all()
for user in users:
    if user.staffPins.pins:
        user.payment_pin = make_password(user.payment_pin)
        # user.save()
        print(f"Updated payment pin for user: {user.email}")
    else:
        print(f"No payment pin set for user: {user.email}")
# for user in users:
#     if user.payment_pin:
#         user.payment_pin = make_password(user.payment_pin)
#         # user.save()
#         print(f"Updated payment pin for user: {user.email}")
#     else:
#         print(f"No payment pin set for user: {user.email}")