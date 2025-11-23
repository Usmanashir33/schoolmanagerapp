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
    if user.has_attr('staffpins'):
        if user.staffpins.pins:
            user.staffpins.pins = make_password(user.staffpins.pins)
            # user.save()
            print(f"Updated staffpins.pins pin for user: {user.email}")
        else:
            print(f"No staffpins.pins pin set for user: {user.email}")
    else:
# for user in users:
#     if user.payment_pin:
#         user.payment_pin = make_password(user.payment_pin)
#         # user.save()
#         print(f"Updated payment pin for user: {user.email}")
#     else:
#         print(f"No payment pin set for user: {user.email}")