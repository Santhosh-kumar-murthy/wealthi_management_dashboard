import pymysql
from pymysql.cursors import DictCursor

from database_config import db_config


class SettingsController:
    def __init__(self):
        self.conn = pymysql.connect(**db_config, cursorclass=DictCursor)
        self.create_settings_table()

    def create_settings_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS wealthi_settings (
                                mqtt_host VARCHAR(255),
                                mqtt_port VARCHAR(255),
                                mqtt_topic VARCHAR(255)
                            )
                        ''')
            self.conn.commit()

    def get_settings(self):
        with self.conn.cursor() as cursor:
            cursor.execute('''SELECT * FROM wealthi_settings''')
            settings = cursor.fetchone()
        return settings

    def update_settings(self, mqtt_host, mqtt_port, mqtt_topic):
        with self.conn.cursor() as cursor:
            # Check if there is an existing settings record
            cursor.execute('''SELECT COUNT(*) as count FROM wealthi_settings''')
            result = cursor.fetchone()

            if result['count'] > 0:
                # Update the existing record
                cursor.execute('''
                    UPDATE wealthi_settings
                    SET mqtt_host = %s, mqtt_port = %s, mqtt_topic = %s
                ''', (mqtt_host, mqtt_port, mqtt_topic))
            else:
                # Insert a new record
                cursor.execute('''
                    INSERT INTO wealthi_settings (mqtt_host, mqtt_port, mqtt_topic)
                    VALUES (%s, %s, %s)
                ''', (mqtt_host, mqtt_port, mqtt_topic))

            # Commit the changes to the database
            self.conn.commit()
