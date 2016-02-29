# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2
import json

class JsonWriterPipeline(object):
    def __init__(self):
        self.file = open('items.jl', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

class PostgresPipeline(object):
    def __init__(self, db_name, db_user, db_host, db_port, db_password):
        try: 
            self.db = psycopg2.connect("dbname="+db_name+" user="+db_user+" host="+db_host+" port="+db_port+" password="+db_password)
        except psycopg2.DatabaseError as e:
            print(e)
            exit(42)
        # Living a dangerous live
        self.db.autocommit = True
        self.cursor = self.db.cursor()

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.get('DATABASE')
        return cls(
            db_name = db_settings.get('database'),
            db_user = db_settings.get('username'),
            db_host = db_settings.get('host'),
            db_port = db_settings.get('port'),
            db_password = db_settings.get('password'),
        )

    def open_spider(self, spider):
        self.tbl_name = spider.name
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS "+self.tbl_name+" (url text PRIMARY KEY, visited timestamp, published timestamp, title text, description text, text text, author text[], keywords text[]);")

    def close_spider(self, spider):
        self.db.commit()
        self.db.close()

    def process_item(self, item, spider):
        try:
            # Needs postgresql version >= 9.5 for UPSERT, else remove "ON CONFLICT ..." line and handle duplicates
            self.cursor.execute(
                "INSERT INTO "+self.tbl_name+" "+
                    "VALUES (%s, %s, %s ,%s ,%s, %s, %s, %s) "+
                    "ON CONFLICT DO NOTHING ;"
                    ,(
                    item['url'],
                    item['visited'],
                    item['published'],
                    item['title'],
                    item['description'],
                    item['text'],
                    item['author'],
                    item['keywords'],
                )
            )
        except psycopg2.DatabaseError as e:
            print(e)
        return item
