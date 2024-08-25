from datetime import datetime

import bcrypt
import pymysql
from pymysql.cursors import DictCursor

from database_config import db_config


class ManagementUserController:
    def __init__(self):
        self.conn = pymysql.connect(**db_config, cursorclass=DictCursor)
        self.create_users_table()

    def drop_all_tables(self):
        with self.conn.cursor() as cursor:
            cursor.execute('''DROP TABLE alice_blue_instruments;
                DROP TABLE angel_instruments;
                DROP TABLE brokers;
                DROP TABLE instruments_load_logs;
                DROP TABLE management_users;
                DROP TABLE observable_instruments;
                DROP TABLE settings;
                DROP TABLE shoonya_instruments;
                DROP TABLE system_logs;
                DROP TABLE wealthi_settings;
                DROP TABLE zerodha_instruments;
                '''
            )

    def create_users_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS management_users (
                                management_user_id INT AUTO_INCREMENT PRIMARY KEY,
                                management_user_name VARCHAR(255),
                                management_user_email VARCHAR(255),
                                management_user_password VARCHAR(255),
                                management_user_role INT,
                                management_user_phone VARCHAR(255),
                                management_user_status INT,
                                management_user_created_at DATE,
                                management_user_created_by INT
                            )''')
        self.conn.commit()

    def insert_user(self, name, email, password, role, phone, status, created_by):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        with self.conn.cursor() as cursor:
            query = '''INSERT INTO management_users (management_user_name, management_user_email, management_user_password,management_user_role, management_user_phone, management_user_status, management_user_created_at, management_user_created_by)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(query, (
                name, email, hashed_password, role, phone, status, datetime.now().strftime('%Y-%m-%d'), created_by
            ))
        self.conn.commit()

    def update_user(self, user_id, name=None, email=None, password=None, role=None, phone=None, status=None):
        with self.conn.cursor() as cursor:
            query = 'UPDATE management_users SET '
            params = []
            if name:
                query += 'management_user_name = %s, '
                params.append(name)
            if email:
                query += 'management_user_email = %s, '
                params.append(email)
            if password:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                query += 'management_user_password = %s, '
                params.append(hashed_password)
            if role:
                query += 'management_user_role = %s, '
                params.append(role)
            if phone:
                query += 'management_user_phone = %s, '
                params.append(phone)
            if status is not None:
                query += 'management_user_status = %s, '
                params.append(status)

            query = query.rstrip(', ') + ' WHERE management_user_id = %s'
            params.append(user_id)

            cursor.execute(query, params)
        self.conn.commit()

    def activate_user(self, user_id):
        self.update_user(user_id, status=1)

    def deactivate_user(self, user_id):
        self.update_user(user_id, status=0)

    def get_all_users(self):
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM management_users')
            return cursor.fetchall()

    def get_active_users(self):
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM management_users WHERE management_user_status = 1')
            return cursor.fetchall()

    def get_inactive_users(self):
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM management_users WHERE management_user_status = 0')
            return cursor.fetchall()

    def login(self, email, password):
        with self.conn.cursor() as cursor:
            query = 'SELECT * FROM management_users WHERE management_user_email = %s'
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            if user and bcrypt.checkpw(password.encode('utf-8'), user['management_user_password'].encode('utf-8')):
                return user
            else:
                return None
