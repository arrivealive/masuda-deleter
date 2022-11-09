from contextlib import nullcontext
from multiprocessing.sharedctypes import Value
from socketserver import BaseRequestHandler
from sre_constants import MAX_UNTIL
from tkinter.messagebox import NO

#from time import sleep

import os
import re
import pickle
import json
import time
from datetime import datetime, timedelta
from calendar import timegm
from typing import Tuple
import urllib.parse

from django.conf import settings
from django.utils.timezone import make_aware
from masuda import const
from masudaapi.models import Post, HatenaUser, Progress, StopCommand, Delete_Post, Delete_Later_Check
from masudaapi.lib.MasudaRequest import MasudaRequest
from masudaapi.lib import user_getter

import logging

class Masuda:
    val = []
    progress = None
    info = ''
    error_message = ''
    cookie_path = os.path.join(settings.BASE_DIR, "masudaapi/files/cookies.pkl")
    piddir_path = os.path.join(settings.BASE_DIR, "masudaapi/files/pidfile")
    pidfile_path = ''
    parser = None
    request = None
    
    def __init__(self):
        self.request = MasudaRequest()
        
    def set_error_message(self, message):
        self.error_message = message
    
    def set_progress(self, progress:Progress):
        self.progress = progress

    def login(self):
        result = self.request.relogin()
        if not result:
            result = self.request.initial_login(const.HATENA["ID"], const.HATENA["PASSWORD"])
        
        return result
    
    def use_progress(action:str):
        def _use_progress(func):
            def wrapper(self, *args, **kwargs):
                overview = ''
                total = 1
                pidfile_name = action.lower()
                if action in ['DELETE_ONE', 'RELOAD', 'EMPTY']:
                    id = args[0]

                    post = Post.objects.filter(id=id).first()
                    if not post:
                        return False
                    
                    if action == 'DELETE_ONE':
                        overview = f'Delete {post.masuda_id}'
                    elif action == 'EMPTY':
                        overview = f'Empty {post.masuda_id}'
                    elif action == 'RELOAD':
                        overview = f'Reload {post.masuda_id}'
                    
                    pidfile_name += str(id)

                elif action == 'FETCH':
                    page_from = args[0]
                    page_to = args[1]
                    total = (page_to - page_from + 1) * const.HATENA['PAGE_SIZE'] # approximation
                    overview = f'Fetch page {page_from} - {page_to}'

                #create progress
                user = user_getter.get()
                if not self.progress:
                    self.progress = Progress(
                        user = user,
                        total = total,
                        processed = 0,
                        action = Progress.ACTIONS[action],
                        overview = overview,
                        pid = str(os.getpid()),
                        status = Progress.STATUS.PENDING
                    )
                else:
                    self.progress.user = user
                    self.progress.total = total
                    self.progress.processed = 0
                    self.progress.action = Progress.ACTIONS[action]
                    self.progress.overview = overview
                    self.progress.pid = str(os.getpid())
                    self.progress.status = Progress.STATUS.PENDING

                
                if not self.save_pidfile(pidfile_name):
                    self.progress.status = Progress.STATUS.ERROR
                    self.progress.memo = 'Other process is running.'
                    self.progress.save()
                    return False
                
                self.progress.pidfile = self.pidfile_path
                self.progress.save()

                result = func(self, *args, **kwargs)
                
                # progress finished
                if result:
                    if self.info:
                        self.progress.memo = self.info
                    self.progress.status = Progress.STATUS.PROCESSED
                else:
                    if self.progress.status != Progress.STATUS.STOPPED:
                        if self.error_message:
                            self.progress.memo = self.error_message
                        self.progress.status = Progress.STATUS.ERROR
                self.progress.save()
            
                return result
            return wrapper
        return _use_progress

    def stop_gracefully(self, memo = ''):
        if type(self.progress) is Progress:
            stop_command = StopCommand.objects.filter(progress=self.progress, is_executed=False).first()
            if stop_command:
                stop_command.is_executed = True
                stop_command.save()
                self.progress.status = Progress.STATUS.STOPPED
                self.progress.memo = memo
                self.progress.save()
                return True
        return False
    
    def save_file(self, name, source):
        path = os.path.join(settings.BASE_DIR, "masudaapi/files/" + name)
        with open(path, 'w') as f:
            f.write(source)
    
    def save_pidfile(self, file_name):
        pidfile_path = os.path.join(settings.BASE_DIR, "masudaapi/files/pidfile/" + file_name + ".pid")
        try:
            with open(pidfile_path, 'x') as f:
                f.write(str(os.getpid()))
                self.pidfile_path = pidfile_path
        except FileExistsError:
            return False
        return True

    @use_progress('FETCH')
    def fetch(self, page_from:int, page_to:int):
        #login
        result = self.login()
        if not result:
            self.progress.status = Progress.STATUS.ERROR
            self.progress.memo = 'Login failed.'
            self.progress.save()
            return result

        # progress start
        self.progress.status = Progress.STATUS.PROCESSING
        self.progress.save()

        # get pages
        result = self.get_pages(page_from, page_to)
        
        # progress finished
        if result:
            self.progress.total = self.progress.processed # fixed total amount
            self.progress.save()
        else:
            pass # The progress has been finished when get_pages() returns False

        return result
    

    def get_pages(self, page_from:int, page_to:int):
        for i in range(page_from, page_to + 1):
            # stop command
            if (self.stop_gracefully(f'Stopped before page {i}.')):
                return False
                
            self.get_page(i)

        return True
    
    def get_page(self, page:int):
        posts = self.request.get_page(page)
        if len(posts) > 0:
            bookmark_counts = self.request.get_bookmarks(posts.keys())

            for masuda_id, post in posts.items():
                bookmark_count = ''
                if masuda_id in bookmark_counts:
                    bookmark_count = bookmark_counts[masuda_id]
                posts[masuda_id]['bookmark_count'] = bookmark_count

            self.save_posts(posts)

    
    def save_posts(self, posts:dict):
        # may be deleted
        self.check_to_be_deleted(posts)

        # save posts
        for post in posts.values():
            self.save_post(post)

            # save progress
            if type(self.progress) is Progress:
                self.progress.processed += 1
                self.progress.save()
    
    def save_post(self, post:dict):
        user = user_getter.get()

        # save post
        Post.objects.update_or_create(
            masuda_id=post['masuda_id'], defaults={
                'masuda_id': post['masuda_id'],
                'title' : post['title'],
                'body' :post['body'],
                'posted_at' : make_aware(post['posted_at']),
                'response_count' : post['response_count'],
                'bookmark_count' : post['bookmark_count'],
                'may_be_deleted' : False,
                'user' : user
            }
        )
    
    def check_to_be_deleted(self, fetched_posts:dict):
        # 獲れ増の最新日時と最古日時の範囲で既存のデータを検索する。
        # 獲れ増に存在せずDBに存在するレコードは削除されたかもしれないフラグを立てる。
        min_date = datetime.now()
        max_date = datetime(1990, 1, 1, 0, 0, 0)
        # max and min posted times of fetched posts
        for value in fetched_posts.values():
            if value['posted_at'] > max_date:
                max_date = value['posted_at']
            if value['posted_at'] < min_date:
                min_date = value['posted_at']
        # get posts from db between posted times of fetched posts
        old_post_masuda_ids = Post.objects.filter(posted_at__range=(make_aware(min_date), make_aware(max_date))).order_by('id').values('id', 'masuda_id')
        old_post_masuda_id_dict = {v['masuda_id']:v['id'] for v in old_post_masuda_ids}

        # remove from dict of db posts if it is fetched this time
        for masuda_id in fetched_posts.keys():
            # this post still exists
            if masuda_id in old_post_masuda_id_dict:
                old_post_masuda_id_dict.pop(masuda_id)
 
        # may be deleted
        for id in old_post_masuda_id_dict.values():
            post = Post.objects.filter(id=id, may_be_deleted=False).first()
            if post:
                post.may_be_deleted = True
                post.save()

    @use_progress('RELOAD')
    def reload(self, id):
        #graceful stop
        if self.stop_gracefully('Stopped before start.'):
            return False

        # progress start
        self.progress.status = Progress.STATUS.PROCESSING
        self.progress.save()

        # get pages
        result = self.update_post(id)
        
        # progress finished
        if result:
            self.progress.processed += 1
            self.progress.save()

        return result

    def update_post(self, id):
        post = Post.objects.filter(id = id).first()
        if not post:
            self.error_message = 'Post not found.'
            return False
        new_post = self.request.get_post(post.masuda_id)

        if new_post:
            post.title = new_post['title']
            post.body = new_post['body']
            post.response_count = new_post['response_count']

            time.sleep(3) # 何か3秒ほしい感じ
            bookmarks = self.request.get_bookmarks([post.masuda_id])
            post.bookmark_count = bookmarks[post.masuda_id]
            post.save()
        else:
            self.info = 'The post may be deleted.'
            post.may_be_deleted = True
            post.save()
        return True

    @use_progress('EMPTY')
    def empty(self, id):
        post = Post.objects.filter(id=id).first()
        if not post:
            self.error_message = 'Post not found.'
            return False
        
        #login
        result = self.login()
        if not result:
            self.progress.status = Progress.STATUS.ERROR
            self.progress.memo = 'Login failed.'
            self.progress.save()
            return result
        
        #graceful stop
        if self.stop_gracefully('Stopped before start.'):
            return False

        # progress start
        self.progress.status = Progress.STATUS.PROCESSING
        self.progress.save()

        # space masuda
        result = self.request.space_masuda(post.masuda_id)

        if result:
            post.title = ''
            post.body = ' '
            post.save()
            self.progress.processed += 1
            self.progress.save()
        
        return result
    
    @use_progress('DELETE_ONE')
    def delete_one(self, id):
        #login
        result = self.login()
        if not result:
            self.progress.status = Progress.STATUS.ERROR
            self.progress.memo = 'Login failed.'
            self.progress.save()
            return result

        #graceful stop
        if self.stop_gracefully('Stopped before start.'):
            return False

        # progress start
        self.progress.status = Progress.STATUS.PROCESSING
        self.progress.save()

        # delete a post
        result = self.delete_post(id)
        if result:
            self.progress.processed += 1
            self.progress.save()
        
        return result

    @use_progress('DELETE')
    def delete(self):
        result = self.create_delete_posts_from_checks()
        
        delete_posts = Delete_Post.objects.filter(progress=self.progress).select_related('post')
        if not delete_posts:
            self.progress.status = Progress.STATUS.ERROR
            self.progress.memo = 'Posts to be deleted are not found.'
            self.progress.save()
            return False
        self.progress.total = delete_posts.count()
        
        self.progress.overview = 'Delete ' + str(delete_posts.count()) + ' posts'
        self.progress.save()
        #login
        result = self.login()
        if not result:
            self.progress.status = Progress.STATUS.ERROR
            self.progress.memo = 'Login failed.'
            self.progress.save()
            return result
        # progress start
        self.progress.status = Progress.STATUS.PROCESSING
        self.progress.save()

        # delete posts
        deleted_list = []
        delete_from_only_db = []
        for delete_post in delete_posts:
            # graceful stop
            if self.stop_gracefully('Stopped gracefully. Deleted: ' + ', '.join(deleted_list)):
                return False
            result = self.delete_post(delete_post.post.id)
            delete_post.refresh_from_db()
            if result:
                delete_post.is_executed = 1
                delete_post.save()
                deleted_list.append(delete_post.masuda_id)
            self.progress.processed += 1
            self.progress.save()
            #FIXME
            if self.info and (re.search(r'may have been deleted', self.info) or re.search(r'not found', self.info)):
                delete_from_only_db.append(delete_post.masuda_id)
        
        if len(delete_from_only_db) > 0:
            self.info = 'Delete from only DB because these posts have been deleted or are not found. :' + ','.join(delete_from_only_db)

        return True

    def create_delete_posts_from_checks(self):
        user = user_getter.get()
        checks = Delete_Later_Check.objects.filter(post__user=user).select_related('post')
        if checks.count() == 0:
            return False
        delete_posts = [Delete_Post(
                masuda_id=check.post.masuda_id,
                progress=self.progress,
                post=check.post,
                user=user
        ) for check in checks]
        Delete_Post.objects.bulk_create(delete_posts)
        return True
    
    def delete_post(self, id):
        post = Post.objects.filter(id=id).first()
        if not post:
            self.error_message = 'Post not found.'
            return False
        
        if post.may_be_deleted:
            post.delete()
            self.info = 'Delete from only DB because this post may have been deleted.'
            return True

        result = self.request.delete(post.masuda_id)
        if result:
            self.info = self.request.get_info()
            post.delete()
        else:
            self.error_message = self.request.get_error_message()
        return result

    def __del__(self):
        if type(self.progress) is Progress:
            if self.progress.status == Progress.STATUS.PROCESSING or self.progress.status == Progress.STATUS.PENDING:
                self.progress.status = Progress.STATUS.ERROR
                if self.error_message:
                    self.progress.memo = self.error_message
                self.progress.save()
        if self.pidfile_path:
            if os.path.isfile(self.pidfile_path):
                os.remove(self.pidfile_path)

