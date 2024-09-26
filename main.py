import pymysql
from flask import Flask, render_template, session, redirect, request, url_for, flash
from pya3 import *
from pymysql.cursors import DictCursor

from controllers.instruments_controller import InstrumentsController
from controllers.instruments_get_controller import InstrumentsGetController
from controllers.logs_controller import LogsController
from controllers.mqtt_publisher import MqttPublisher
from controllers.settings_controller import SettingsController
from controllers.trades_controller import TradesController
from database_config import db_config
from setup import *

app = Flask(__name__)

app.secret_key = 'BAD_SECRET_KEY'


@app.route('/')
def index():
    if session.get('is_logged_in') is True:
        return redirect(url_for('dashboard'))
    else:
        return redirect('login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_controller = ManagementUserController()
        email = request.form['email']
        password = request.form['password']
        result = user_controller.login(email, password)
        if result:
            session['is_logged_in'] = True
            session['user_details'] = result
            return redirect(url_for('dashboard'))
        else:
            flash('Login Failed. Please check your credentials.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if session.get('is_logged_in') is True:
        return render_template('dashboard.html')
    else:
        flash('Please login to use the platform.', 'danger')
        return redirect(url_for('login'))


@app.route('/users')
def users():
    if session.get('is_logged_in') is True:
        user_controller = ManagementUserController()
        all_users = user_controller.get_all_users()
        return render_template('users.html', all_users=all_users)
    else:
        flash('Please login to use the platform.', 'danger')
        return redirect(url_for('login'))


@app.route('/today_trades')
def today_trades():
    if session.get('is_logged_in') is True:
        trades_controller = TradesController()
        fut_trades = trades_controller.get_fut_trades()
        return render_template('today_trades.html', fut_trades=fut_trades)
    else:
        flash('Please login to use the platform.', 'danger')
        return redirect(url_for('login'))


@app.route('/today_trades_hastar')
def today_trades_hastar():
    if session.get('is_logged_in') is True:
        trades_controller = TradesController()
        hastar_trades = trades_controller.get_hastar_trades()
        return render_template('today_trades_hastar.html', fut_trades=hastar_trades)
    else:
        flash('Please login to use the platform.', 'danger')
        return redirect(url_for('login'))


@app.route('/close_trade')
def close_trade():
    pos_id = request.args.get('pos_id')
    mqtt_publisher = MqttPublisher()
    mqtt_msg = json.dumps({
        "type": "force_exit",
        "pos_id": pos_id
    }, default=str)
    mqtt_publisher.publish_payload(mqtt_msg)
    flash("message sent to exit position : id : " + pos_id)
    return redirect(url_for('today_trades'))


@app.route('/users_add')
def users_add():
    return render_template('users_add.html')


@app.route('/brokers')
def brokers():
    broker_controller = BrokerController()
    settings_controller = SettingsController()
    all_brokers = broker_controller.get_all_brokers()
    active_time_frame = broker_controller.get_time_frame_settings()['active_time_frame']
    settings = settings_controller.get_settings()
    return render_template('brokers.html', all_brokers=all_brokers, active_time_frame=active_time_frame,
                           settings=settings)


@app.route('/update_mqtt_config')
def update_mqtt_config():
    mqtt_host = request.args.get('mqtt_host')
    mqtt_port = request.args.get('mqtt_port')
    mqtt_topic = request.args.get('mqtt_topic')
    settings_controller = SettingsController()
    settings_controller.update_settings(mqtt_host, mqtt_port, mqtt_topic)
    flash('mqtt config updated !', 'success')
    return redirect(url_for('brokers'))


@app.route('/broker/update_system_use_status')
def broker_update_system_use_status():
    broker_id = request.args.get('b_id')
    status = request.args.get('status')
    broker_controller = BrokerController()
    broker_controller.broker_change_system_use_status(broker_id, status)
    flash('Status changed !', 'success')
    return redirect(url_for('brokers'))


@app.route('/change_active_time_frame')
def change_active_time_frame():
    active_time_frame = request.args.get('active_time_frame')
    broker_controller = BrokerController()
    broker_controller.change_active_time_frame(active_time_frame)
    flash('time frame updated !', 'success')
    return redirect(url_for('brokers'))


@app.route('/broker/update_config_params', methods=['GET', 'POST'])
def broker_update_config_params():
    broker_id = request.args.get('b_id')
    broker_controller = BrokerController()
    if request.method == 'POST':
        config_params = request.form['config_params']
        time_frame_params = request.form['time_frame_params']
        broker_controller.update_broker(broker_id=broker_id, broker_config_params=config_params,
                                        broker_time_frames=time_frame_params)
        flash('Updated successfully', 'success')
        return redirect(url_for('broker_update_config_params') + '?b_id=' + broker_id)
    else:
        broker_details = broker_controller.get_broker_by_id(broker_id=broker_id)
        return render_template('broker_config_params.html', broker_details=broker_details)


@app.route('/instruments')
def instruments():
    return render_template('instruments.html')


@app.route('/add_observable_instrument', methods=['GET', 'POST'])
def add_observable_instrument():
    instrument_manager = InstrumentsGetController()
    if session.get('is_logged_in') is True:
        if request.method == 'POST':
            zerodha_trading_symbol = request.form['zerodha_trading_symbol']
            angel_trading_symbol = request.form['angel_trading_symbol']
            shoonya_trading_symbol = request.form['shoonya_trading_symbol']
            alice_blue_symbol = request.form['alice_blue_symbol']
            search_key = request.form['search_key']
            instrument_manager.add_observable_instrument(zerodha_trading_symbol, angel_trading_symbol,
                                                         shoonya_trading_symbol, alice_blue_symbol, search_key)
            flash('Added successfully', 'success')
            return redirect(url_for('observable_instruments'))
        else:
            shoonya_instruments = instrument_manager.get_idx_shoonya()
            angel_instruments = instrument_manager.get_idx_angel()
            zerodha_instruments = instrument_manager.get_idx_zerodha()
            alice_blue_instruments = instrument_manager.get_idx_alice_blue()
            return render_template('add_observable_instrument.html',
                                   zerodha_instruments=zerodha_instruments,
                                   angel_instruments=angel_instruments,
                                   shoonya_instruments=shoonya_instruments,
                                   alice_blue_instruments=alice_blue_instruments)
    else:
        flash('Please login to use the platform.', 'danger')
        return redirect(url_for('login'))


def zerodha_instrument_setup():
    instrument_load_manager = InstrumentsController()
    broker_manager = BrokerController()
    kite_config = json.loads(broker_manager.get_broker_by_id(1)['broker_config_params'])
    instrument_load_manager.clear_zerodha_instruments()
    status, log_text = instrument_load_manager.load_zerodha_instruments(kite_config)
    logs_controller = LogsController()
    logs_controller.insert_log(process_status=status, process_log=log_text, broker_id=1)


def angel_one_instrument_setup():
    instrument_load_manager = InstrumentsController()
    instrument_load_manager.clear_angel_instruments()
    status, log_text = instrument_load_manager.load_angel_instruments()
    logs_controller = LogsController()
    logs_controller.insert_log(process_status=status, process_log=log_text, broker_id=2)


def shoonya_instrument_setup():
    instrument_load_manager = InstrumentsController()
    instrument_load_manager.clear_shoonya_instruments()
    status, log_text = instrument_load_manager.load_shoonya_instruments()
    logs_controller = LogsController()
    logs_controller.insert_log(process_status=status, process_log=log_text, broker_id=3)


def alice_blue_instrument_setup():
    instrument_load_manager = InstrumentsController()
    instrument_load_manager.clear_alice_blue_instruments()
    status, log_text = instrument_load_manager.load_alice_blue_instruments()
    logs_controller = LogsController()
    logs_controller.insert_log(process_status=status, process_log=log_text, broker_id=4)


def async_zerodha_instrument_setup():
    thread = threading.Thread(target=zerodha_instrument_setup)
    thread.start()


def async_angel_one_instrument_setup():
    thread = threading.Thread(target=angel_one_instrument_setup)
    thread.start()


def async_shoonya_instrument_setup():
    thread = threading.Thread(target=shoonya_instrument_setup)
    thread.start()


def async_alice_blue_instrument_setup():
    thread = threading.Thread(target=alice_blue_instrument_setup)
    thread.start()


@app.route('/start_load_instruments')
def start_load_instruments():
    async_zerodha_instrument_setup()
    async_angel_one_instrument_setup()
    async_shoonya_instrument_setup()
    async_alice_blue_instrument_setup()
    flash('Loading instruments in the background.', 'success')
    return redirect(url_for('brokers'))


@app.route('/load_instruments_logs')
def load_instruments_logs():
    log_controller = LogsController()
    all_logs = log_controller.get_all_logs()
    return render_template('load_instrument_logs.html', all_logs=all_logs)


@app.route('/system_logs')
def system_logs():
    log_controller = LogsController()
    all_system_logs = log_controller.get_all_system_logs()
    return render_template('system_logs.html', all_system_logs=all_system_logs)


@app.route('/observable_instruments')
def observable_instruments():
    instruments_controller = InstrumentsGetController()
    all_observable_instruments = instruments_controller.get_observable_instruments()
    print(all_observable_instruments)
    for ins in all_observable_instruments:
        print(ins)
    return render_template('observable_instruments.html', all_observable_instruments=all_observable_instruments)


@app.route('/delete_observable_instrument')
def delete_observable_instrument():
    instrument_id = request.args.get('instrument_id')
    instruments_manager = InstrumentsGetController()
    instruments_manager.delete_observable_instrument(instrument_id)
    flash('Delete successful', 'success')
    return redirect(url_for('observable_instruments'))


@app.route('/setup')
def setup():
    user_setup()
    broker_setup()
    insert_default_time_frame()
    flash('Setup successful', 'success')
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Logout successful', 'success')
    return redirect(url_for('login'))


def get_nearby_fut():
    connection = pymysql.connect(**db_config, cursorclass=DictCursor)
    instruments_controller = InstrumentsGetController()
    all_observable_instruments = instruments_controller.get_observable_instruments()
    future_instrument_list = []
    for instrument in all_observable_instruments:
        with connection.cursor() as cursor:
            query = """
                SELECT * 
                FROM alice_blue_instruments 
                WHERE (alice_instrument_type = 'FUTIDX' OR alice_instrument_type = 'IF') AND alice_symbol = %s
                AND DATE(alice_expiry_date) >= curdate() ORDER BY alice_expiry_date ASC LIMIT 1;
                """
            cursor.execute(query, instrument['search_key'])
            # Fetching all results
            results = cursor.fetchone()
            instrument_detail = {
                "alice": results,
            }
            future_instrument_list.append(instrument_detail)

            query = """
                SELECT * FROM zerodha_instruments WHERE zerodha_segment IN ('NFO-FUT', 'BFO-FUT') AND zerodha_name = %s
                AND DATE(zerodha_expiry) >= curdate() ORDER BY zerodha_expiry ASC LIMIT 1; """
            cursor.execute(query, instrument['search_key'])
            # Fetching all results
            results = cursor.fetchone()
            instrument_detail = {
                "Zerodha": results,
            }
            future_instrument_list.append(instrument_detail)

            query = """SELECT * FROM angel_instruments WHERE angel_instrument_type='FUTIDX' AND angel_name = %s
                            AND DATE(angel_expiry) >= curdate() ORDER BY angel_expiry ASC LIMIT 1; """
            cursor.execute(query, instrument['search_key'])
            # Fetching all results
            results = cursor.fetchone()
            instrument_detail = {
                "angel": results,
            }
            future_instrument_list.append(instrument_detail)

            query = """SELECT * FROM shoonya_instruments WHERE shoonya_instrument_type='FUTIDX' AND shoonya_symbol = %s
                            AND DATE(shoonya_expiry) >= curdate() ORDER BY shoonya_expiry ASC LIMIT 1; """
            cursor.execute(query, instrument['search_key'])
            # Fetching all results
            results = cursor.fetchone()
            instrument_detail = {
                "shoonya": results,
            }
            future_instrument_list.append(instrument_detail)

    return future_instrument_list


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
