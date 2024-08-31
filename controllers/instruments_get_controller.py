import pymysql
from pymysql.cursors import DictCursor

from database_config import db_config


class InstrumentsGetController:
    def __init__(self):
        self.conn = pymysql.connect(**db_config, cursorclass=DictCursor)
        self.create_observable_instruments_table()

    def create_observable_instruments_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS observable_instruments (
                                o_id int(11) NOT NULL AUTO_INCREMENT,
                                zerodha_instrument_token int(11),
                                zerodha_exchange_token int(11),
                                zerodha_trading_symbol varchar(255),
                                zerodha_name varchar(255),
                                zerodha_expiry date,
                                zerodha_lot_size int(11),
                                zerodha_instrument_type varchar(255),
                                zerodha_segment varchar(255),
                                zerodha_exchange varchar(255),
                                angel_token int(11),
                                angel_symbol varchar(255),
                                angel_name varchar(255),
                                angel_expiry date,
                                angel_lot_size int(11),
                                angel_instrument_type varchar(255),
                                angel_exchange_segment varchar(255),
                                angel_trading_symbol varchar(255),
                                shoonya_exchange varchar(255),
                                shoonya_token int(11),
                                shoonya_lot_size int(11),
                                shoonya_name varchar(255),
                                shoonya_trading_symbol varchar(255),
                                shoonya_expiry date,
                                shoonya_instrument_type varchar(255),
                                shoonya_option_type varchar(255),
                                PRIMARY KEY (o_id),
                                alice_exchange VARCHAR(255),
                                alice_exchange_segment VARCHAR(255),
                                alice_expiry_date DATE,
                                alice_formatted_ins_name VARCHAR(255),
                                alice_instrument_type VARCHAR(255),
                                alice_lot_size INT,
                                alice_option_type VARCHAR(255),
                                alice_pdc DECIMAL(10, 2) NULL,
                                alice_strike_price DECIMAL(10, 2),
                                alice_symbol VARCHAR(255),
                                alice_token VARCHAR(255),
                                alice_trading_symbol VARCHAR(255),
                                search_key VARCHAR(255)
                            )
                        ''')
            self.conn.commit()

    def get_idx_shoonya(self):
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM shoonya_instruments WHERE shoonya_instrument_type=%s',
                           'index')
            shoonya_instruments = cursor.fetchall()
        return shoonya_instruments

    def get_idx_angel(self):
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM angel_instruments WHERE angel_instrument_type=%s',
                           'AMXIDX')
            angel_instruments = cursor.fetchall()
        return angel_instruments

    def get_idx_alice_blue(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM alice_blue_instruments WHERE alice_exchange_segment = %s OR alice_exchange_segment = %s',
                ('nse_idx', 'bse_idx'))
            alice_instruments = cursor.fetchall()
        return alice_instruments

    def get_idx_zerodha(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM zerodha_instruments WHERE zerodha_segment = %s", 'INDICES')
            angel_instruments = cursor.fetchall()
        return angel_instruments

    def get_observable_instruments(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM observable_instruments")
            observable_instruments = cursor.fetchall()
        return observable_instruments

    def delete_observable_instrument(self, o_id):
        print()
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM observable_instruments WHERE o_id = %s", o_id)
            self.conn.commit()

    def add_observable_instrument(self, zerodha_trading_symbol, angel_trading_symbol, shoonya_trading_symbol,
                                  alice_symbol, search_key):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM zerodha_instruments WHERE zerodha_trading_symbol = %s",
                           zerodha_trading_symbol)
            zerodha_instrument = cursor.fetchone()
            cursor.execute("SELECT * FROM angel_instruments WHERE angel_symbol = %s",
                           angel_trading_symbol)
            angel_instrument = cursor.fetchone()
            cursor.execute("SELECT * FROM shoonya_instruments WHERE shoonya_trading_symbol = %s",
                           shoonya_trading_symbol)
            shoonya_instrument = cursor.fetchone()
            cursor.execute("SELECT * FROM alice_blue_instruments WHERE alice_symbol = %s",
                           alice_symbol)
            alice_instrument = cursor.fetchone()
            # Insert into observable_instruments table
            cursor.execute('''
                           INSERT INTO observable_instruments (
                               zerodha_instrument_token, zerodha_exchange_token,
                                zerodha_trading_symbol, zerodha_name,
                               zerodha_expiry, zerodha_lot_size,
                                zerodha_instrument_type, zerodha_segment,
                                 zerodha_exchange, angel_token, 
                                 angel_symbol, angel_name,
                                  angel_expiry, angel_lot_size, 
                                  angel_instrument_type,angel_exchange_segment,
                                   angel_trading_symbol, shoonya_exchange, 
                                   shoonya_token, shoonya_lot_size,
                               shoonya_name, shoonya_trading_symbol, 
                               shoonya_expiry, shoonya_instrument_type, 
                               shoonya_option_type,alice_exchange,
                                alice_exchange_segment, alice_expiry_date, 
                                alice_formatted_ins_name, alice_instrument_type, 
                                alice_lot_size, alice_option_type,
                                 alice_pdc, alice_strike_price, 
                                alice_symbol,  
                                alice_token, alice_trading_symbol,
                                search_key
                           ) VALUES (
                           %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                             %s, %s, %s, %s, %s, %s,
                              %s, %s, %s, %s, %s, %s,
                               %s,%s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s,
                                 %s,%s)
                       ''', (
                zerodha_instrument['zerodha_instrument_token'], zerodha_instrument['zerodha_exchange_token'],
                zerodha_instrument['zerodha_trading_symbol'], zerodha_instrument['zerodha_name'],
                zerodha_instrument['zerodha_expiry'], zerodha_instrument['zerodha_lot_size'],
                zerodha_instrument['zerodha_instrument_type'], zerodha_instrument['zerodha_segment'],
                zerodha_instrument['zerodha_exchange'], angel_instrument['angel_token'],
                angel_instrument['angel_symbol'], angel_instrument['angel_name'], angel_instrument['angel_expiry'],
                angel_instrument['angel_lot_size'], angel_instrument['angel_instrument_type'],
                angel_instrument['angel_exchange_segment'], angel_instrument['angel_symbol'],
                shoonya_instrument['shoonya_exchange'], shoonya_instrument['shoonya_token'],
                shoonya_instrument['shoonya_lot_size'], shoonya_instrument['shoonya_symbol'],
                shoonya_instrument['shoonya_trading_symbol'], shoonya_instrument['shoonya_expiry'],
                shoonya_instrument['shoonya_instrument_type'], shoonya_instrument['shoonya_option_type'],
                alice_instrument['alice_exchange'], alice_instrument['alice_exchange_segment'],
                alice_instrument['alice_expiry_date'], alice_instrument['alice_formatted_ins_name'],
                alice_instrument['alice_instrument_type'], alice_instrument['alice_lot_size'],
                alice_instrument['alice_option_type'], alice_instrument['alice_pdc'],
                alice_instrument['alice_strike_price'], alice_instrument['alice_symbol'],
                alice_instrument['alice_token'],
                alice_instrument['alice_trading_symbol'], search_key
            ))
            self.conn.commit()
