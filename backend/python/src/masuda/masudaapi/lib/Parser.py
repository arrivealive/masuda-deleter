import re
import time
from datetime import datetime, timedelta
from calendar import timegm
from typing import Tuple

import json
from bs4 import BeautifulSoup

import logging

class Parser:

    def check_login(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        gmenus = soup.select('div#bannersub .gmenu')
        result = False
        for gmenu in gmenus:
            text = gmenu.get_text(strip=True)
            if text == 'ログアウト':
                result = True
        return result

    def parse(self, html) -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        daycontents = soup.select('div.day')

        posts = {}
        
        for daycontent in daycontents:
            day = daycontent.select_one('h2').get_text()
            sections = daycontent.select('div.body>div.section')
            for section in sections:
                h3 = section.select_one('h3').extract()
                # title
                id, title = self.__parse_title(h3)
                try:
                    section.select_one('.afc').decompose()
                except AttributeError:
                    pass
                section.select_one('p.share-button').decompose()
                # footer
                sectionfooter = section.select_one('p.sectionfooter').extract()
                response_count = self.__parse_sectionfooter(sectionfooter)
                keywords = section.select('a.keyword')
                for keyword in keywords:
                    keyword.unwrap()
                # convert p, li, dd, dt to \n
                p = section.select('p, li, dd, dt')
                for content in p:
                    content.insert_after("\n")
                    content.unwrap()
                text = section.get_text()
                m = re.match(r'^([\d]{14})', id)

                # 13/32 24:60:60
                tt = time.strptime(m.group(), "%Y%m%d%H%M%S")
                posted_at = datetime(1970, 1, 1) + timedelta(seconds=timegm(tt))
                
                # posted_at = datetime.strptime(m.group(), '%Y%m%d%H%M%S')

                posts[id] = {
                    'masuda_id': id,
                    'title': title,
                    'body': text,
                    'posted_at': posted_at,
                    'response_count': response_count,
                }
                
        return posts

    def __parse_title(self, h3:BeautifulSoup) -> Tuple[str, str]:
        try:
            h3.select_one('a.edit').decompose()
        except AttributeError:
            pass
        button = h3.find('button')
        if button:
            button.decompose()
        href = h3.select_one('a:nth-child(1)').extract()['href']
        id = re.search(r'\/([\d]{14,})\/?$', href).group(1)
        # id = h3.select_one('a:nth-child(1)').extract()['href'].replace('/', '')
        title = h3.get_text()
        return id, title

    def __parse_sectionfooter(self, sectionfooter:BeautifulSoup):
        sectionfooter.select_one('a:nth-child(1)').decompose()
        response = sectionfooter.select_one('a:nth-child(1)').extract().get_text()
        response_count = re.search(r'[0-9]+', response).group()
        try:
            sectionfooter.select_one('a.mention-link').decompose()
        except AttributeError:
            pass
        try:
            sectionfooter.select_one('span.wide').decompose()
        except AttributeError:
            pass
        
        # time = sectionfooter.get_text(strip = True).replace('|', '')
        return response_count
    
    def parse_bapi_response(self, html) -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        bookmarks = json.loads(text)
        bookmark_counts = {}
        for u, count in bookmarks.items():
            m = re.search(r'[\d]+$', u)
            if not m:
                continue
            bookmark_counts[m[0]] = count

        return bookmark_counts
