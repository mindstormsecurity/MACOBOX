import os
import psutil
import re
import subprocess
from collections import namedtuple

_ntuple_diskusage = namedtuple('usage', 'percentage used free')
_ntuple_ramusage = namedtuple('usage', 'percentage used free')
mount_path = '/media/orangepi/usb'

def get_disk_usage(path):

    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize

    percentage_used = int((used / total) * 100)

    free = round(free / (1024**3), 2)
    used = round(used / (1024**3), 2)
    return _ntuple_diskusage(percentage_used, used, free)

def get_ram_usage():
    mem = psutil.virtual_memory()
    total_ram_gb = mem.total / (1024**3)
    used_ram_gb = (mem.total - mem.available) / (1024**3)
    free_ram_gb = mem.available / (1024**3)
    percentage_ram_used = int((used_ram_gb / total_ram_gb) * 100)

    total_ram_gb = round(total_ram_gb, 2)
    used_ram_gb = round(used_ram_gb, 2)
    free_ram_gb = round(free_ram_gb, 2)

    return _ntuple_ramusage(percentage_ram_used,used_ram_gb,free_ram_gb)

def get_cpu_temperature():
    cpu_temperatures = psutil.sensors_temperatures()
    for sensor, temps in cpu_temperatures.items():
        if 'cpu' in sensor.lower():
            for temp in temps:
                if temp.label == '':
                    return round(temp.current,2)
    return None

def execute_start_transfer_usb(file_name, file_type):
    if file_type == "uart":
        file_base_path = 'uart_dump/logs/'
    elif file_type == "spi":
        file_base_path = 'spi_dump/binaries/'
    elif file_type == "i2c":
        file_base_path = 'i2c_dump/binaries/'
    else:
        return {"error": "Unsupported file type"}

    if not os.path.exists(file_base_path):
        return {"error": "Unsupported file type"}

    mount_path = '/media/orangepi/usb'
    if not os.path.exists(mount_path):
        return {"error": "No device mounted at /media/usb"}

    source_file_path = os.path.join(file_base_path, file_name)
    print(source_file_path)
    if not os.path.exists(source_file_path):
        return {"error": "Source file does not exist"}

    try:
        #shutil.copy(source_file_path, mount_path)
        command = ['sudo', 'cp', source_file_path, mount_path]
        subprocess.run(command, check=True)
        return {"success": "File transferred successfully"}
    except Exception as e:
        return {"error": f"Error transferring file: {str(e)}"}
    
def is_safe_filename_log(filename):
    pattern = r'^log_\d{8}-\d{6}\.txt$'
    return bool(re.match(pattern, filename))

def is_safe_filename_bin(filename):
    pattern = r'^\d{8}-\d{6}\.bin$'
    return bool(re.match(pattern, filename))

def is_device_mounted():
    return os.path.ismount(mount_path)
