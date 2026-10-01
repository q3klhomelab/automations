import os
from datetime import datetime
import shutil
import filecmp
import subprocess

source_folder = ""
bkp_folder = ""
log_file = ""

def write_log(message, file=log_file):
    with open(file, "a", encoding="utf-8") as f:
        f.write(f'{datetime.now().strftime("%Y-%m-%d - %H:%M:%S")} {message}\n')

if not os.path.exists(bkp_folder):
    os.makedirs(bkp_folder, exist_ok=True)

for root, _, files in os.walk(source_folder):
    for file in files:
        source_file = os.path.join(root, file)
        rel_source_folder = os.path.relpath(root, source_folder)
        destination_folder = os.path.join(bkp_folder, rel_source_folder)
        destination_file = os.path.join(destination_folder, file)
        
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        
        try:
            if not os.path.exists(destination_file) or not filecmp.cmp(source_file, destination_file, shallow=True):
                shutil.copy2(source_file, destination_file)
        except Exception as error:
            write_log(f"File copy error: {error}")
            
write_log("Backup complete")

try:
    subprocess.run(["sync"], check=True)
    subprocess.run(["systemctl", "stop", "mnt-bkp_disk.mount"], check=True)
except subprocess.CalledProcessError as error:
    write_log(f"Disk unmount error: {error}\nPossible data corruption")