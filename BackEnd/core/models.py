import datetime
from django.db import models
from django.db import models

# Create your models here.
from django.db import models
import shortuuid
from authUser.models import User
import os , uuid
from django.utils.translation import gettext_lazy as _  
from datetime import datetime
from django.db import transaction

# Create your models here.
class NumberCounter(models.Model):
    last_number = models.PositiveIntegerField(default=0)
    def __str__(self):
        return str(self.last_number)
    
    

def generate_unique_admission_number(tag,prefix=''):
    year = str(datetime.now().year)[-2:]
    with transaction.atomic():
        counter, created = NumberCounter.objects.select_for_update().get_or_create(id=1)
        counter.last_number += 1
        counter.save()
        unique_number = str(counter.last_number).zfill(4)

    return f"{tag}/{prefix}/{year}/{unique_number}" if prefix else f"{tag}/{year}/{unique_number}"

