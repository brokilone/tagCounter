import argparse
import datetime
import json
import logging
import re
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlparse

import yaml
from sqlalchemy import Column, String, DATE
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///sqlalchemy_tags.db')


class TagInfo(Base):
    __tablename__ = 'tag_info'
    url = Column(String(100), primary_key=True)
    domain = Column(String(100), nullable=False)
    check_date = Column(DATE, nullable=False)
    tag_dictionary = Column(String, nullable=False)

    @staticmethod
    def persist(tag_dictionary, url):
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        now = datetime.date.today()
        second_level_domain = urlparse(url).hostname.split('.')[-2]
        entry = TagInfo(domain=second_level_domain, url=url, check_date=now, tag_dictionary=json.dumps(tag_dictionary))
        session.add(entry)
        session.commit()
        session.close()

    @staticmethod
    def find_by_url(site_url):
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        found = session.get(TagInfo, {"url": site_url})
        session.close()
        return found


Base.metadata.create_all(engine)


def configure_logger():
    strfmt = '[%(asctime)s] -  %(message)s'
    datefmt = '%Y-%m-%d  %H:%M:%S'
    logging.basicConfig(filename='requests.log',
                        filemode='a',
                        format=strfmt,
                        datefmt=datefmt,
                        level=logging.DEBUG)

    return logging.getLogger('tagCounter')


logger = configure_logger()


class MyHTMLParser(HTMLParser):
    def __init__(self, tag_info):
        super().__init__()
        self.tag_dictionary = dict()
        self.tag_info = tag_info

    def handle_endtag(self, tag):
        if tag in self.tag_dictionary:
            self.tag_dictionary[tag] = self.tag_dictionary[tag] + 1
        else:
            self.tag_dictionary[tag] = 1

    @staticmethod
    def load_site(url, timeout):
        with urllib.request.urlopen(url, timeout=timeout) as conn:
            return conn.read()

    @staticmethod
    def format_url(site_url):
        if not re.match('(?:http|ftp|https)://', site_url):
            return 'https://{}'.format(site_url)
        return site_url

    def process_get(self, site_url):
        found = self.tag_info.find_by_url(site_url)
        if not found:
            data = self.load_site(site_url, 60).decode('utf-8')
            self.feed(data)
            self.tag_info.persist(self.tag_dictionary, site_url)
            logger.info(site_url)

    def process_view(self, site_url):
        found = self.tag_info.find_by_url(site_url)
        if found:
            print(found.tag_dictionary)
        else:
            print('Данные по {} отсутствуют. Для загрузки данных используйте --get "{}"'.format(site_url, site_url))

    def check_alias(self, site_url):
        with open('synonyms.yaml') as file:
            aliases = yaml.safe_load(file)
            if site_url in aliases:
                return aliases[site_url]
            return self.format_url(site_url)

    def add_to_yaml(self, alias_to_add):
        key = alias_to_add[0]
        value = self.format_url(alias_to_add[1])
        with open('synonyms.yaml') as file:
            aliases = yaml.safe_load(file)
            if not aliases:
                aliases = {}
        with open('synonyms.yaml', 'w') as file:
            aliases[key] = value
            yaml.dump(aliases, file)

    def del_from_yaml(self, alias_to_del):
        with open('synonyms.yaml') as file:
            aliases = yaml.safe_load(file)
        with open('synonyms.yaml', 'w') as file:
            if alias_to_del in aliases:
                del aliases[alias_to_del]
                yaml.dump(aliases, file)

    def process_synonyms(self, args):
        alias_to_add = args.add
        alias_to_del = args.dl
        if alias_to_add:
            self.add_to_yaml(alias_to_add)
        if alias_to_del:
            self.del_from_yaml(alias_to_del)


def create_synonyms():
    file = open('synonyms.yaml', 'a+')
    aliases = dict()
    aliases['ydx'] = 'https://yandex.com'
    aliases['goo'] = 'https://google.com'
    aliases['sof'] = 'https://stackoverflow.com'
    yaml.dump(aliases, file)
    file.close()


def main():
    parser = argparse.ArgumentParser(
        prog='Программа для подсчета и сохранения количества тегов на сайте',
        description='Требуется передать команду (подсчет или просмотр) и url сайта либо его алиас')
    parser.add_argument('--get', help='Принимает url сайта или его alias для обработки')
    parser.add_argument('--view', help='Принимает url сайта или его alias для росмотра результата обработки')
    parser.add_argument('--add', nargs=2, help='Добавляет или заменяет alias для сайта')
    parser.add_argument('--dl', help='Добавляет или заменяет alias для сайта')
    create_synonyms()
    args = parser.parse_args()
    tag_info = TagInfo()
    html_parser = MyHTMLParser(tag_info)
    html_parser.process_synonyms(args)
    site_url = args.get

    if site_url:
        site_url = html_parser.check_alias(site_url)
        html_parser.process_get(site_url)
    else:
        site_url = args.view
        if site_url:
            site_url = html_parser.check_alias(site_url)
            html_parser.process_view(site_url)


if __name__ == '__main__':
    main()
