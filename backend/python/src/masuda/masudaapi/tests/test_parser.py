from django.test import TestCase
from django.conf import settings
from masudaapi.lib import Parser
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

from masudaapi.tests.BaseTests import BaseTests

class ParserTests(BaseTests):
    def setUp(self):
        super().setUp()
        self.parser = Parser.Parser()

    def test_check_login(self):
        path = os.path.join(settings.BASE_DIR, "masudaapi/tests/files/home.html")
        with open(path) as f:
            html = f.read()
        result = self.parser.check_login(html)
        self.assertTrue(result)
    
    def test_parse(self):
        path = ParserTests.get_file_path('1.html')
        with open(path) as f:
            html = f.read()
        posts = self.parser.parse(html)
        self.assertEqual(25, len(posts))
        values = [value for value in posts.values()]
        r = True
        masuda_ids = [masuda_id for masuda_id in posts.keys()]
        dummy_posts = DummyPost.objects.filter(masuda_id__in=masuda_ids)
        self.assertEqual(25, len(dummy_posts))
        jst = tz.gettz('Asia/Tokyo')
        for dummy_post in dummy_posts:
            post = posts[dummy_post.masuda_id]
            r *= post['masuda_id'] == dummy_post.masuda_id
            if dummy_post.masuda_id == '20220509161549':
                r *= 'カレッジ叔父ハードウェア今日トレーナー意図。' in post['title']
            if dummy_post.masuda_id == '20220702030148':
                r *= '敵対的なダニ憲法副本質的な。' in post['body']
                r *= '細かい本質的な器官溝溝バケツ試してみる。' in post['body']
                r *= '部隊文言倫理あった欠乏動物編組ジャム。' in post['body']
                r *= 'ノートささやき感謝する画面プラスチックキャビネット。' in post['body']
                r *= '発生する販売脊椎クルー持っていました。見落とす舗装同行。' in post['body']
                r *= '中世改善デッド。保証金再現する編組教会ピック。' in post['body']

            r *= int(post['response_count']) == dummy_post.response_count
            # print(make_aware(post['posted_at']), dummy_post.posted_at.astimezone(jst))
            r *= make_aware(post['posted_at']) == dummy_post.posted_at.astimezone(jst)
        self.assertTrue(r)
        #     post.masuda_id

    # def test_parse_title(self):
    #     path = ParserTests.get_file_path('title.html')
    #     with open(path) as f:
    #         html = f.read()
    #     soup = BeautifulSoup(html, 'html.parser')
    #     id, title = self.parser.parse_title(soup)
    #     self.assertEqual('20220123045657', id)
    #     self.assertEqual('🐧ポッチャマ', title)

