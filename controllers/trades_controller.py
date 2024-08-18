import pymysql
from pymysql.cursors import DictCursor

from database_config import db_config


class TradesController:
    def __init__(self):
        self.conn = pymysql.connect(**db_config, cursorclass=DictCursor)

    def get_fut_trades(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM fut_positions WHERE DATE(position_entry_time) = CURDATE();")
            today_fut_trades = cursor.fetchall()
        return today_fut_trades

    def get_opt_trades(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM opt_positions WHERE DATE(position_entry_time) = CURDATE();")
            today_opt_trades = cursor.fetchall()
        return today_opt_trades
