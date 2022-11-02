import os
import pickle
import time
from calendar import timegm
import urllib.parse

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException

from django.conf import settings
from masuda import const

import logging

from masudaapi.lib.Parser import Parser

class MasudaRequest:
    info = ''
    error_message = ''
    cookie_path = ''
    parser = None
    user_id = ''

    def __init__(self):
        self.parser = Parser()
        self.set_cookie_name(const.HATENA['ID'])
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--no-sandbox")
        # for "selenium.common.exceptions.WebDriverException: Message: unknown error: session deleted because of page crash"
        options.add_argument('--disable-dev-shm-usage') 

        self.driver = webdriver.Chrome(options = options)

    def get_cookie_path(self):
        return self.cookie_path
    
    def set_cookie_path(self, path):
        self.cookie_path = path

    def set_cookie_name(self, name):
        self.set_cookie_path(os.path.join(settings.BASE_DIR, f"masudaapi/files/{name}.pkl"))

    def initial_login(self, login_id, password):
        url = const.HATENA['LOGIN_URL']

        self.driver.get(url)
        time.sleep(0.5)

        key_element = self.driver.find_element(By.NAME, 'key') 
        password_element = self.driver.find_element(By.NAME, 'password') 

        key_element.clear()
        key_element.send_keys(login_id)
        password_element.clear()
        password_element.send_keys(password)

        key_element.submit()
        time.sleep(0.5)

        result = self.check_login()
        if result:
            # cookieの保存
            pickle.dump(self.driver.get_cookies(), open(self.cookie_path, "wb"))
        return result

    def relogin(self):
        if not os.path.isfile(self.cookie_path):
            return False
        cookies = pickle.load(open(self.cookie_path, "rb"))
        self.driver.get(const.HATENA['ANOND_URL'])
        time.sleep(0.5)
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        
        result = self.check_login()
        if not result:
            os.remove(self.cookie_path)

        return result
    
    def check_login(self):
        self.driver.get(const.HATENA['ANOND_URL'] + '/')
        time.sleep(1)
        html = self.driver.page_source

        result = self.parser.check_login(html)
        if (result):
            self.user_id = const.HATENA['ID']

        return result

    def get(self, url):
        self.driver.get(url)
        return self.driver.page_source

    def get_page(self, page, user_id = None):
        if user_id is None:
            user_id = const.HATENA['ID']
        if user_id:
            user_id = user_id + '/'
        self.driver.get(const.HATENA['ANOND_URL'] + '/' + user_id + '?page=' + str(page))
        time.sleep(2)
        WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located)
        html = self.driver.page_source

        posts = self.parser.parse(html)
        return posts

    def get_post(self, masuda_id):
        self.driver.get(const.HATENA['ANOND_URL'] + '/' + masuda_id)
        time.sleep(1)
        WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located)
        html = self.driver.page_source
        posts = self.parser.parse(html)
        if posts:
            return posts[masuda_id]
        else:
            return None

    def get_bookmarks(self, masuda_ids:list) -> dict:
        # make urls for hatena bookmark api
        urls = [urllib.parse.quote(os.path.join(const.HATENA['ANOND_URL'], id), safe='') for id in masuda_ids]
        url = const.HATENA['BOOKMARK_API_URL'] + '?url=' + '&url='.join(urls)
        self.driver.get(url)
        time.sleep(2)
        source = self.driver.page_source
        bookmark_counts = self.parser.parse_bapi_response(source)
        return bookmark_counts

    def space_masuda(self, masuda_id):
        self.driver.get(const.HATENA['ANOND_URL'] + '/' + const.HATENA['ID'] + '/edit?id=' + masuda_id)
        WebDriverWait(self.driver, 3).until(EC.presence_of_all_elements_located)
        time.sleep(0.5)

        title_element = self.driver.find_element(By.ID, 'text-title') 
        body_element = self.driver.find_element(By.ID, 'text-body')
        submit_button = self.driver.find_element(By.ID, 'submit-button')
        # title_element.clear()
        title_element.send_keys(Keys.CONTROL + 'a', Keys.BACKSPACE)
        # body_element.clear()
        body_element.send_keys(Keys.CONTROL + 'a', Keys.BACKSPACE)
        body_element.send_keys(' ')
        submit_button.click()
        time.sleep(1)

        return True

    def delete(self, masuda_id):
        # check existance
        self.driver.get(const.HATENA['ANOND_URL'] + '/' + masuda_id)
        WebDriverWait(self.driver, 3).until(EC.presence_of_all_elements_located)
        time.sleep(0.5)
        try:
            element = self.driver.find_element(By.CLASS_NAME, "edit")
        except NoSuchElementException as e:
            self.info = 'Masuda not found.'
            return True

        self.driver.get(const.HATENA['ANOND_URL'] + '/' + const.HATENA['ID'] + '/edit?id=' + masuda_id)
        time.sleep(0.5)
        delete_button = self.driver.find_element(By.NAME, 'delete')
        delete_button.click()
        wait = WebDriverWait(self.driver,10)
        try:
            wait.until(EC.alert_is_present())
            Alert(self.driver).accept()
            time.sleep(0.5)

        except Exception as e: # error of alert
            self.error_message = e
            return False
        
        return True
    
    def save_screenshot(self, name = ''):
        if name == '':
            name = "Website.png"
        # capture the screen and save to a file
        path = os.path.join(settings.BASE_DIR, "masudaapi/files/" + name)
        self.driver.save_screenshot(path)
        
    def get_info(self):
        return self.info

    def get_error_message(self):
        return self.error_message


    def save_file(self, name, source):
        path = os.path.join(settings.BASE_DIR, "masudaapi/files/" + name)
        with open(path, 'w') as f:
            f.write(source)

    def __del__(self):
        self.driver.quit()
