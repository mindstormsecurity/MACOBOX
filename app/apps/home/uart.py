# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from flask_socketio import SocketIO, emit
import subprocess
import threading
import time
import os 
import serial
from threading import Thread
import datetime
from werkzeug.utils import safe_join


device_path = '/dev/ttyACM0'
log_path = 'uart_dump/logs/'

socketio = SocketIO()
uart_running = True
ser = None
serial_thread = None

def serial_reader():
    global ser
    while True:
        if ser and ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            socketio.emit('serial_data', data)

def uart_handle_start_serial(baudrate):
    global ser,serial_thread
    if os.path.exists(device_path):
        ser = serial.Serial(device_path, baudrate)
    else:
        socketio.emit('serial_data', f"Device {device_path} not present.")
        return "",500

    if not ser.is_open:
        ser.open()
    if not serial_thread or not serial_thread.is_alive():
        print("starting thread")
        serial_thread = Thread(target=serial_reader)
        serial_thread.daemon = True
        serial_thread.start()


def send_data_to_serial(text):
    global ser
    if ser and ser.is_open:
        print("writing")
        ser.write(text.encode('utf-8'))
    else:
        socketio.emit('serial_data', "Serial port not available.")
        

def execute_save_uart_logs(text):
    date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = os.path.join(log_path, f"log_{date}.txt")

    print(text)
    try:
        with open(file_name, 'w') as file:
            file.write(text)

        return f"File succesfully saved: {file_name}"
    except Exception as e:
        raise RuntimeError(f"An error occurred while saving the file: {str(e)}")

def execute_get_uart_logs():
    log_files = [f for f in os.listdir(log_path) if os.path.isfile(os.path.join(log_path, f))]
    return log_files


def get_uart_log_content(file_name):
    file_path = safe_join(log_path, file_name)

    if not os.path.exists(file_path):
        return jsonify(success=False, error="File not found"), 404

    # Leggi il contenuto del file
    with open(file_path, 'r') as file:
        content = file.read()
    return content


def execute_delete_uart_log(file_name):
    file_path = safe_join(log_path, file_name)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Log {file_path} has been succesfully deleted.")
        except OSError as e:
            print(f"Errore removing {file_path}: {e}")
    else:
        print(f"{file_path} does not exist.")
