from django.test import TestCase
from django.conf import settings
from masudaapi.lib import Masuda, MasudaRequest, Parser
from masudaapi.models import Post, Progress, HatenaUser
from masudaapi.tests.factories import HatenaUserFactory, PostFactory, ProgressFactory, StopCommandFactory
from dummy.models import Post as DummyPost
from datetime import datetime
from django.utils.timezone import make_aware
from random import randrange
from faker import Faker
from unittest.mock import patch
from masuda import const
import time
from datetime import datetime, timedelta
from calendar import timegm
import os
from django.contrib.auth.models import User
import unittest
from bs4 import BeautifulSoup
from dateutil import tz
from django.core import management

# from masudaapi.tests.BaseTests import BaseTests
# Create your tests here.

# class GetUserMockResponse:
#     def __init__(self):
#         self.user = HatenaUserFactory()

HATENA = {
    'ID' : 'masuda',
    'PASSWORD' : 'veVTBujSKoAB',
    'ANOND_URL' : 'http://127.0.0.1:8107/dummy',
    'LOGIN_URL' : 'http://127.0.0.1:8107/dummy/login',
    'BOOKMARK_API_URL' : 'http://127.0.0.1:8107/dummy/bookmark',
    'PAGE_SIZE' : 25
}

class BaseTests(TestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        const.HATENA = HATENA

    def setUp(self):
        pass
        # self.auth_user = User.objects.create_user('masuda', 'masuda@example.com', 'veVTBujSKoAB')

    @classmethod
    def get_file_path(cls, name):
        return os.path.join(settings.BASE_DIR, f"masudaapi/tests/files/{name}")
    
