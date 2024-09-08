from contextlib import closing

import pymysql
from pymysql.cursors import DictCursor

from database_config import db_config


class TradesController:
    def __init__(self):
        self.conn = pymysql.connect(**db_config, cursorclass=DictCursor)
        self.create_positions_table()

    def create_positions_table(self):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS positions (
                                position_id INT AUTO_INCREMENT PRIMARY KEY,
                                observable_instrument_id INT,
                                zerodha_instrument_token INT,
                                zerodha_trading_symbol VARCHAR(255),
                                zerodha_name VARCHAR(255),
                                zerodha_exchange VARCHAR(255),
                                angel_token INT,
                                angel_symbol VARCHAR(255),
                                angel_name VARCHAR(255),
                                angel_exchange VARCHAR(255),
                                shoonya_token INT,
                                shoonya_trading_symbol VARCHAR(255),
                                shoonya_name VARCHAR(255),
                                shoonya_exchange VARCHAR(255),
                                alice_token VARCHAR(255),
                                alice_trading_symbol VARCHAR(255),
                                alice_name VARCHAR(255),
                                alice_exchange VARCHAR(255),
                                instrument_position_type INT COMMENT 
                                '1 = FUT BUY\r\n2 = FUT SELL\r\n3 = OPT BUY\r\n4 = OPT SELL',
                                position_type INT COMMENT 
                                '1 = LONG\r\n2 = SHORT',
                                position_entry_time DATETIME,
                                position_entry_price FLOAT,
                                position_exit_time DATETIME,
                                position_exit_price FLOAT,
                                profit FLOAT,
                                lot_size INT,
                                position_qty INT,
                                time_frame VARCHAR(255),
                                expiry DATE  
                            )
                        ''')
            self.conn.commit()

    def get_fut_trades(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM positions WHERE DATE(position_exit_time) = CURDATE() OR position_exit_time IS NULL;")
            today_fut_trades = cursor.fetchall()
        return today_fut_trades

    def get_opt_trades(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM opt_positions WHERE DATE(position_exit_time) = CURDATE() OR position_exit_time IS NULL;")
            today_opt_trades = cursor.fetchall()
        return today_opt_trades
