import datetime

import pymysql
from pymysql.cursors import DictCursor

from database_config import db_config


class LogsController:
    def __init__(self):
        self.conn = pymysql.connect(**db_config, cursorclass=DictCursor)
        self.create_instruments_load_logs_table()
        self.create_system_logs_table()

    def create_system_logs_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS system_logs (
                                log_id INT AUTO_INCREMENT PRIMARY KEY,
                                log_content LONGTEXT,
                                log_date_time DATETIME
                            )
                        ''')
            self.conn.commit()

    def create_instruments_load_logs_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS instruments_load_logs (
                                log_id INT AUTO_INCREMENT PRIMARY KEY,
                                process_status VARCHAR(255),
                                process_log LONGTEXT,
                                process_time DATETIME,
                                broker_id INT
                            )
                        ''')
            self.conn.commit()

    def insert_log(self, process_status, process_log, broker_id):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                   INSERT INTO instruments_load_logs (process_status, process_log, process_time,broker_id)
                   VALUES (%s, %s, %s,%s)
               ''', (process_status, process_log, datetime.datetime.now(), broker_id))
            self.conn.commit()

    def get_all_logs(self):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                   SELECT * FROM instruments_load_logs JOIN brokers ON instruments_load_logs.broker_id = brokers.broker_id
               ''')
            return cursor.fetchall()

    def get_all_system_logs(self):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                          SELECT * FROM system_logs
                      ''')
            return cursor.fetchall()
