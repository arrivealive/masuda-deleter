from django.test import TestCase
from django.conf import settings
from masudaapi.lib import Masuda, MasudaRequest, Parser
from masudaapi.models import Post, Progress, HatenaUser, Delete_Post
from masudaapi.tests.factories import HatenaUserFactory, PostFactory, ProgressFactory, StopCommandFactory, DeletePostFactory, DeleteLaterCheckFactory
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
import random

from masudaapi.tests.BaseTests import BaseTests


class MasudaTests(BaseTests):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # cls.request = MasudaRequest.MasudaRequest()
        # cls.cookie_path = BaseTests.get_file_path('__test.' + const.HATENA['ID'] + '.pkl')
        
    def setUp(self):
        super().setUp()
        self.masuda = Masuda.Masuda()
        self.user = HatenaUserFactory()
        self.masuda.request.set_cookie_path(BaseTests.get_file_path('__test.' + const.HATENA['ID'] + '.pkl'))
    
    def setUpFetch(self):
        
        self.posts = []
        masuda_ids = [
            '20130602091452',
            '20130608215243',
            '20150112213310',
            '20150329135041',
            '20150515062621',
            '20151126114217',
            '20200322013203',
            '20200326024006',
            '20210526062951',
            '20220901180049',
        ]

        for i in range(0, 10):
            post = {
                'masuda_id': masuda_ids[i], 
                'title': f'タイトル{i}', 
                'body': f'本文{i}', 
                'posted_at': make_aware(datetime.strptime(masuda_ids[i], '%Y%m%d%H%M%S')), 
                'user': self.user,
                'response_count': 0,
                'bookmark_count': 0
            }
            self.posts.append(PostFactory(**post))
        
        self.posts[9].body = '📞🐘'
        
        fetched_masuda_ids = [
            '20200322013203', #update 6 0
            # '20200326024006', #may be deleted 7
            '20200328162832', #create 1
            '20210526062951' #update 8 2
            ]
        self.new_posts = {}
        
        for i in range(0, 3):
            # print (type(datetime.strptime(fetched_masuda_ids[i], '%Y%m%d%H%M%S')))
            tt = time.strptime(fetched_masuda_ids[i], "%Y%m%d%H%M%S")
            posted_at = datetime(1970, 1, 1) + timedelta(seconds=timegm(tt))
            self.new_posts[fetched_masuda_ids[i]] = {
                'masuda_id': fetched_masuda_ids[i], 
                'title': f'タイトル{i}{i}', 
                'body': f'本文{i}{i}', 
                'posted_at': posted_at, 
                'response_count': i * 2,
                'bookmark_count': i
            }
        
        # self.progress = ProgressFactory(
        #     total=3,
        #     processed=0,
        #     action=Progress.ACTIONS.FETCH,
        #     status=Progress.STATUS.PENDING,
        #     user=self.user
        # )
        # self.masuda.progress = self.progress
    
    def test_login(self):
        result = self.masuda.login()
        self.assertTrue(result)
        user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.hatena_id, const.HATENA['ID'])
        user.delete()
        user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
        self.assertIsNone(user)
        result = self.masuda.login()
        self.assertTrue(result)
        user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.hatena_id, const.HATENA['ID'])
    
    def test_stop_gracefully(self):
        r = self.masuda.stop_gracefully('test')
        self.assertFalse(r)
        progress = ProgressFactory(**{
            'total':1,
            'processed':0,
            'action':Progress.ACTIONS.RELOAD,
            'status':0,
            'user':self.user
        })
        self.masuda.progress = progress
        r = self.masuda.stop_gracefully('test')
        self.assertFalse(r)
        stop_command = StopCommandFactory(**{
            'is_executed': False,
            'progress': progress
        })
        r = self.masuda.stop_gracefully('test')
        self.assertTrue(r)
        progress.refresh_from_db()
        stop_command.refresh_from_db()
        self.assertTrue(stop_command.is_executed)
        self.assertEqual(progress.status, Progress.STATUS.STOPPED)
        self.assertEqual(progress.memo, 'test')
    

    def test_get_page(self):
        if not self.masuda.login():
            self.fail('login failed.')
        self.masuda.get_page(2)
        masuda_ids = ['20170126023015', '20150806201800', '20110606014217']
        no_ids = [
            '20110603092752', # page 3
            '20170227000924' # page 1
        ]
        posts = Post.objects.filter(masuda_id__in=masuda_ids).order_by('-posted_at')
        self.assertEqual(len(posts), 3)
        dposts = DummyPost.objects.filter(masuda_id__in=masuda_ids).order_by('-posted_at')
        r = True
        for post, dpost in zip(posts, dposts):
            print(post.bookmark_count , dpost.bookmark_count)
            r *= post.bookmark_count == dpost.bookmark_count
        self.assertTrue(r)

        posts = Post.objects.filter(masuda_id__in=no_ids)
        self.assertEqual(len(posts), 0)

    def test_get_pages(self):
        if not self.masuda.login():
            self.fail('login failed.')
        r = self.masuda.get_pages(2, 3)
        self.assertTrue(r)
        masuda_ids = [
            '20170126023015', '20150806201800', '20110606014217', # page 2
            '20110603092752', # page 3
        ]
        no_ids = [
            '20170227000924', # page 1
            '20061015023322', # page 4
        ]
        posts = Post.objects.filter(masuda_id__in=masuda_ids).order_by('-posted_at')
        self.assertEqual(len(posts), 4)

        posts = Post.objects.filter(masuda_id__in=no_ids).order_by('-posted_at')
        self.assertEqual(len(posts), 0)

        #test stop command
        progress = ProgressFactory(**{
            'total':25,
            'processed':0,
            'action':Progress.ACTIONS.FETCH,
            'status':Progress.STATUS.PENDING,
            'user':self.user
        })
        self.masuda.set_progress(progress)
        r = self.masuda.stop_gracefully('test')
        stop_command = StopCommandFactory(**{
            'is_executed': False,
            'progress': progress
        })
        r = self.masuda.get_pages(1, 1)
        self.assertFalse(r)

    def test_fetch(self):
        r = self.masuda.fetch(1, 2)
        self.assertTrue(r)
        masuda_ids = [
            '20170126023015', '20150806201800', '20110606014217', # page 2
            '20170227000924', # page 1
        ]
        no_ids = [
            '20110603092752', # page 3
            '20061015023322', # page 4
        ]
        posts = Post.objects.filter(masuda_id__in=masuda_ids).order_by('-posted_at')
        self.assertEqual(len(posts), 4)
        posts = Post.objects.filter(masuda_id__in=no_ids).order_by('-posted_at')
        self.assertEqual(len(posts), 0)
        
        #TODO progress test

    def test_reload(self):
        masuda_id = '20200206152807'
        dpost = DummyPost.objects.filter(masuda_id=masuda_id).first()
        post = PostFactory(**{
            'masuda_id': dpost.masuda_id,
            'title': '🧙魔法',
            'body': "🔥ファイア\n❄️ブリザド\n⚡️サンダー",
            'posted_at': dpost.posted_at,
            'response_count': 0,
            'bookmark_count': 0,
            'user': self.user
        })
        self.assertTrue('🧙魔法' in post.title)
        self.assertTrue('🔥ファイア' in post.body)

        r = self.masuda.reload(post.id)
        self.assertTrue(r)
        post.refresh_from_db()
        self.assertEqual(dpost.response_count, post.response_count)
        self.assertEqual(dpost.bookmark_count, post.bookmark_count)
        self.assertFalse('🧙魔法' in post.title)
        self.assertFalse('🔥ファイア' in post.body)
        #TODO progress test

    def test_update_post(self):
        masuda_id = '20200206152807'
        dpost = DummyPost.objects.filter(masuda_id=masuda_id).first()
        post = PostFactory(**{
            'masuda_id': dpost.masuda_id,
            'title': '🧙魔法',
            'body': "🔥ファイア\n❄️ブリザド\n⚡️サンダー",
            'posted_at': dpost.posted_at,
            'response_count': 0,
            'bookmark_count': 0,
            'user': self.user
        })
        self.assertTrue('🧙魔法' in post.title)
        self.assertTrue('🔥ファイア' in post.body)

        r = self.masuda.update_post(post.id)
        self.assertTrue(r)
        post.refresh_from_db()
        self.assertEqual(dpost.response_count, post.response_count)
        self.assertEqual(dpost.bookmark_count, post.bookmark_count)
        self.assertFalse('🧙魔法' in post.title)
        self.assertFalse('🔥ファイア' in post.body)


    # @patch('masuda.const.HATENA', HATENA)
    # @patch('masudaapi.lib.Masuda.get_user', return_value=GetUserMockResponse)
    def test_save_posts(self):
        self.setUpFetch()
            
        self.masuda.save_posts(self.new_posts)

        posts = self.posts

        posts[5].refresh_from_db()
        posts[6].refresh_from_db()
        posts[7].refresh_from_db()
        posts[8].refresh_from_db()
        post = Post.objects.filter(masuda_id='20200328162832').first()

        
        self.assertEqual('masuda', self.user.hatena_id)
        self.assertEqual('本文5', posts[5].body)
        self.assertEqual('本文00', posts[6].body)
        self.assertEqual(False, posts[6].may_be_deleted)
        self.assertEqual(True, posts[7].may_be_deleted)
        self.assertEqual('タイトル11', post.title)
        self.assertEqual(1, post.bookmark_count)
        self.assertEqual(False, post.may_be_deleted)
        self.assertEqual('タイトル22', posts[8].title)
        self.assertEqual(4, posts[8].response_count)
        self.assertEqual(False, posts[8].may_be_deleted)
        self.assertEqual('📞🐘', posts[9].body)
        self.assertEqual(make_aware(datetime(2013, 6, 8, 21, 52, 43)), posts[1].posted_at)

    def test_to_be_deleted(self):
        self.setUpFetch()

        self.masuda.check_to_be_deleted(self.new_posts)
        posts = self.posts

        posts[5].refresh_from_db()
        posts[6].refresh_from_db()
        posts[7].refresh_from_db()
        posts[8].refresh_from_db()
        # post = Post.objects.filter(masuda_id='20200328162832').first()
        self.assertEqual(False, posts[5].may_be_deleted)
        self.assertEqual(False, posts[6].may_be_deleted)
        self.assertEqual(True, posts[7].may_be_deleted)
        self.assertEqual(False, posts[8].may_be_deleted)
        # self.assertEqual(False, post.may_be_deleted)

    def test_delete(self):
        threshold = 0.5
        max = 20
        count = 0
        to_be_deleted = []
        not_to_be_deleted = []
        #全件取得してくる
        dposts = DummyPost.objects.filter(user_id=const.HATENA['ID'])
        for dpost in dposts:
            post = PostFactory(**{
                'masuda_id': dpost.masuda_id,
                'title': dpost.title,
                'body': dpost.body,
                'posted_at': dpost.posted_at,
                'response_count': dpost.response_count,
                'bookmark_count': dpost.bookmark_count,
                'user': self.user
            })
            #無作為に削除対象を選択する
            if count < max:
                if random.random() >= threshold:
                    to_be_deleted.append(post)
                    count += 1
                else:
                    not_to_be_deleted.append(post)
        # TODO progressを作成してmasudaにはめ込み
        # Delete_postを作成する
        for post in to_be_deleted:
            DeleteLaterCheckFactory(**{
                'post': post
            })
        
        # ids = [post.masuda_id for post in to_be_deleted]
        # print([post.masuda_id for post in to_be_deleted])
        # dp = Delete_Post.objects.filter(masuda_id__in=ids)
        # print(dp)
        #実行する
        r = self.masuda.delete()
        if not r:
            print(self.masuda.progress.memo)
        #trueが返ってくることを確認
        self.assertTrue(r)
        #削除対象をpost,dpostから検索して存在しないことを確認
        ids = [post.masuda_id for post in to_be_deleted]
        posts = Post.objects.filter(masuda_id__in=ids)
        self.assertEqual(0, len(posts))
        dposts = DummyPost.objects.filter(masuda_id__in=ids)
        self.assertEqual(0, len(posts))
        #削除対象以外をpost,dpostから検索して存在することを確認
        ids = [post.masuda_id for post in not_to_be_deleted]
        posts = Post.objects.filter(masuda_id__in=ids)
        self.assertEqual(len(ids), len(posts))
        dposts = DummyPost.objects.filter(masuda_id__in=ids)
        self.assertEqual(len(ids), len(posts))
        #deleteを実行してfalseが返ってくることを確認
        r = self.masuda.delete()
        self.assertFalse(r)
        #データ復旧
        self.masuda.request.driver.get(const.HATENA['ANOND_URL'] + '/restore')


    def test_delete_post(self):
        r = self.masuda.login()
        if not r:
            self.fail('Login failed.')
        masuda_id = '20180721161212'
        dpost = DummyPost.objects.filter(masuda_id=masuda_id).first()
        post = PostFactory(**{
            'masuda_id': dpost.masuda_id,
            'title': dpost.title,
            'body': dpost.body,
            'posted_at': dpost.posted_at,
            'response_count': dpost.response_count,
            'bookmark_count': dpost.bookmark_count,
            'user': self.user
        })

        # self.masuda.request.driver.get(const.HATENA['ANOND_URL'] + '/save')
        r = self.masuda.delete_post(post.id)
        self.assertTrue(r)
        dpost = DummyPost.objects.filter(masuda_id=masuda_id).first()
        self.assertIsNone(dpost)
        self.masuda.request.driver.get(const.HATENA['ANOND_URL'] + '/restore')

    def test_create_delete_posts_from_checks(self):
        self.setUpFetch()

        masuda_ids = [
            '20130602091452',
            '20150329135041',
            '20200322013203',
            '20210526062951',
            '20220901180049',
        ]
        posts = Post.objects.filter(masuda_id__in=masuda_ids)
        for post in posts:
            DeleteLaterCheckFactory(**{
                'post':post
            })
        # masuda_ids.append('20200326024006') #not checked
        self.masuda.create_delete_posts_from_checks()
        delete_posts = Delete_Post.objects.filter(post__masuda_id__in=masuda_ids).select_related('post')
        self.assertEqual(5, len(delete_posts))
        r = True
        for delete_post in delete_posts:
            r *= delete_post.post.user_id == self.user.id
            # r *= delete_post.masuda_id != masuda_ids[5]
        self.assertTrue(r)