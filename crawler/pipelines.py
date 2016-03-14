# -*- coding: utf-8 -*-
# Definition of item pipelines
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
import json


class JsonWriterPipeline(object):
    """Pipeline for writing to a file in JSON like notation"""
    def __init__(self):
        self.file = open('items.json', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

class PostgresPipeline(object):
    """Pipeline for writing to a PostgreSQL data base"""

    def __init__(self, db_name, db_user, db_host, db_port, db_password):
        """Initialize the data base"""
        try:
            # Connect to the db using options set in settings.py 
            self.db = psycopg2.connect("dbname="+db_name+" user="+db_user+" host="+db_host+" port="+db_port+" password="+db_password)
        except psycopg2.DatabaseError as e:
            print(e)
            exit(42)
        self.db.autocommit = True
        self.cursor = self.db.cursor()

    @classmethod
    def from_crawler(cls, crawler):
        """Get data base options from settings.py"""
        db_settings = crawler.settings.get('DATABASE')
        return cls(
            db_name = db_settings.get('database'),
            db_user = db_settings.get('username'),
            db_host = db_settings.get('host'),
            db_port = db_settings.get('port'),
            db_password = db_settings.get('password'),
        )

    def open_spider(self, spider):
        """Initialize table when spider opens"""
        self.tbl_name = spider.name
        # Create a table with the same name as the spider if it does not exist already
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS "+self.tbl_name+" (url text PRIMARY KEY, visited timestamp, published timestamp, title text, description text, text text, author text[], keywords text[]);")

    def close_spider(self, spider):
        """Close the connection when spider closes"""
        self.db.commit()
        self.db.close()

    def process_item(self, item, spider):
        """Process items and insert into data base"""
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
