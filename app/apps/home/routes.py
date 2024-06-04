# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, jsonify
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.home.uart import socketio,uart_handle_start_serial, execute_save_uart_logs,execute_get_uart_logs, get_uart_log_content,execute_delete_uart_log,send_data_to_serial
from apps.home.utils import is_device_mounted,get_disk_usage, get_ram_usage, is_safe_filename_log,get_cpu_temperature,execute_start_transfer_usb
import subprocess


@blueprint.route('/index')
@login_required
def index():
    ram_usage_tot = get_ram_usage()
    disk_usage_tot = get_disk_usage("/")
    cpu_temp = get_cpu_temperature()
    return render_template('home/index.html', segment='index',cpu_temp=cpu_temp,used_ram=ram_usage_tot.used,ram_percentage=ram_usage_tot.percentage, used_disk=disk_usage_tot.used, disk_percentage=disk_usage_tot.percentage)


@blueprint.route('/poweroff')
@login_required
def poweroff():
    try:
        subprocess.run(["shutdown", "-h", "now"])
        return "Shutting down."
    except Exception as e:
        return f"Error during system shutdown: {str(e)}"

@blueprint.route('/reboot')
@login_required
def reboot():
    try:
        subprocess.run(["reboot"])
        return "Rebooting."
    except Exception as e:
        return f"Error during system rebooting: {str(e)}"

@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'

        segment = get_segment(request)

        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500



@socketio.on('start_serial')
def handle_start_serial(data):
    baudrate = data['baudrate']
    valid_baudrates = ["110", "300", "600", "1200", "2400", "4800", "9600", "14400", "19200", "38400", "57600", "115200", "128000", "256000"]
    if baudrate in valid_baudrates:
        uart_handle_start_serial(baudrate)
    else:
        return "Invalid baudrate", 400


@socketio.on('send_data_to_serial')
def handle_send_data_to_serial(data):
    text = data['text']
    text=text+"\r"
    send_data_to_serial(text)


@blueprint.route('/save_uart_logs', methods=['POST'])
@login_required
def save_uart_logs():
    text = request.form.get('text')
    try:
        result = execute_save_uart_logs(text)
        if isinstance(result, bytes):  
            result_str = result.decode("utf-8")
        else:  
            result_str = result
        return jsonify({'success': True, 'result': result_str})
    except RuntimeError as e:
        return jsonify({'success': False, 'error': str(e)})

@blueprint.route('/get_uart_logs', methods=['GET'])
@login_required
def get_uart_logs():
    try:
        log_files = execute_get_uart_logs()
        return jsonify(success=True, result=log_files)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@blueprint.route('/get_uart_log_file_content', methods=['GET'])
@login_required
def get_uart_log_file_content():
    file_name = request.args.get('file_name')

    if not file_name:
        return jsonify(success=False, error="File name not provided"), 400

    if not is_safe_filename_log(file_name):
        return jsonify(success=False, error="Unsafe file name"), 400

    try:
        content = get_uart_log_content(file_name)
        return jsonify(success=True, content=content)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@blueprint.route('/delete_uart_log', methods=['POST'])
@login_required
def delete_uart_log():
    try:
        file_name = request.form.get('name')
        
        if is_safe_filename_log(file_name):
            execute_delete_uart_log(file_name)
            
            return jsonify({'success': True, 'message': 'Log succesfully deleted {}'.format(file_name)})
        else:
            return jsonify({'success': False, 'error': 'Wrong file name format.'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@blueprint.route('/transfer_usb', methods=['POST'])
@login_required
def transfer_usb():
    try:
        data = request.get_json()
        nodeName = data.get('nodeName')
        file_type = data.get('file_type')

        result = execute_start_transfer_usb(nodeName,file_type)

        if 'error' in result:
            return jsonify({'success': False, 'message': result['error']}), 500
        
        return jsonify({'success': True, 'message': result})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error during file transfer: {}'.format(str(e))})

@blueprint.route('/is_device_mounted', methods=['GET'])
@login_required
def get_is_device_mounted():
    try:
        result= is_device_mounted()
        return jsonify({'success': True, 'message': result})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error during mount detection: {}'.format(str(e))})


def is_valid_node_name(name):
    import re
    pattern = r'^\d{8}-\d{6}\.bin$'
    return re.match(pattern, name) is not None


def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
