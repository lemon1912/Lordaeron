# from django.test import TestCase

# Create your tests here.
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','Sylvanas.settings')
import django
django.setup()

from django.core.exceptions import ObjectDoesNotExist
from jumpserver.models import Auth_user




print Auth_user.objects.all()


