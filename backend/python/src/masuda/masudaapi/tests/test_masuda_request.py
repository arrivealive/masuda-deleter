from django.test import TestCase
from django.conf import settings
from masudaapi.lib import MasudaRequest
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

from masudaapi.tests.BaseTests import BaseTests
        
class MasudaRequestTests(BaseTests):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # cls.request = MasudaRequest.MasudaRequest()
        cls.cookie_path = BaseTests.get_file_path('__test.' + const.HATENA['ID'] + '.pkl')

    def setUp(self):
        super().setUp()
        self.request = MasudaRequest.MasudaRequest()
        # self.request.set_cookie_path(self.get_file_path('__test.' + const.HATENA['ID'] + '.pkl'))
        self.request.set_cookie_path(self.cookie_path)

    def test_initial_login(self):
        # print(const.HATENA['ID'], const.HATENA['PASSWORD'])
        result = self.request.initial_login(const.HATENA['ID'], 'password')
        self.assertFalse(result)
        result = self.request.initial_login(const.HATENA['ID'], const.HATENA['PASSWORD'])
        self.assertTrue(result)
        self.assertTrue(os.path.isfile(self.request.get_cookie_path()))

    def test_relogin(self):
        result = self.request.check_login()
        self.assertFalse(result)
        result = self.request.relogin()
        self.assertTrue(result)

    def test_set_cookie_name(self):
        self.request.set_cookie_name('aaa')
        c = self.request.get_cookie_path()
        self.assertEqual(c, os.path.join(settings.BASE_DIR, f"masudaapi/files/aaa.pkl"))
    
    def test_check_login(self):
        self.assertFalse(self.request.check_login())
        self.request.initial_login(const.HATENA['ID'], const.HATENA['PASSWORD'])
        self.assertTrue(self.request.check_login())

    def test_get_page(self):
        #ログインせずに2ページ目を取得して2ページ目にある記事が取れているかどうかのみテスト
        posts = self.request.get_page(2, '')
        self.assertEqual(25, len(posts))
        self.assertFalse('20220111211038' in posts)
        self.assertTrue('20200812003706' in posts)
        self.assertTrue('20160826202631' in posts)
        self.assertFalse('20160708215824' in posts)

    def test_get_post(self):
        post = self.request.get_post('20220509161549')
        self.assertEqual('20220509161549', post['masuda_id'])

    def test_get_bookmarks(self):
        masuda_ids = ['20220509161549', '20220911032930', '20220111211038', '00000000000000']
        posts = DummyPost.objects.filter(masuda_id__in=masuda_ids)
        bookmarks = self.request.get_bookmarks(masuda_ids)
        r = True
        for post in posts:
            r *= bookmarks[post.masuda_id] == post.bookmark_count
        r *= bookmarks[masuda_ids[3]] == 0
        self.assertTrue(r)
    
    def test_space_masuda(self):
        # self.request.driver.get(const.HATENA['ANOND_URL'] + '/save')
        r = self.request.initial_login(const.HATENA['ID'], const.HATENA['PASSWORD'])
        if not r:
            self.fail('Login failed.')
        self.request.space_masuda('20191128190205')
        post = self.request.get_post('20191128190205')
        self.assertEqual('', post['title'].strip())
        self.assertEqual('', post['body'].strip())
        self.request.driver.get(const.HATENA['ANOND_URL'] + '/restore')

    def test_delete(self):
        # self.request.driver.get(const.HATENA['ANOND_URL'] + '/save')
        r = self.request.initial_login(const.HATENA['ID'], const.HATENA['PASSWORD'])
        if not r:
            self.fail('Login failed.')
        r = self.request.delete('20120411094947')
        self.assertTrue(r)
        post = self.request.get_post('20120411094947')
        self.assertIsNone(post)

        r = self.request.delete('20120411094947')
        self.assertTrue(r)
        self.assertEqual('Masuda not found.', self.request.get_info())


        post = self.request.get_post('20110808041431')
        self.assertIsNotNone(post)
        
        self.request.driver.get(const.HATENA['ANOND_URL'] + '/restore')

    def tearDown(self) -> None:
        return super().tearDown()
    
    @classmethod
    def tearDownClass(cls):
        # os.remove(cls.cookie_path)
        super().tearDownClass()
