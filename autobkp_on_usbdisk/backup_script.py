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

def bkp_with_os(source, destination):
    errors = 0
    for root, _, files in os.walk(source):
        for file in files:
            source_file = os.path.join(root, file)
            rel_source_folder = os.path.relpath(root, source)
            destination_folder = os.path.join(destination, rel_source_folder)
            destination_file = os.path.join(destination_folder, file)
            
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            
            try:
                if not os.path.exists(destination_file) or not filecmp.cmp(source_file, destination_file, shallow=True):
                    shutil.copy2(source_file, destination_file)
            except Exception as error:
                errors += 1
                write_log(f"File copy error: {error}")
    if errors:
        write_log(f"Backup completed with {errors} errors, check the log file")
    else:
        write_log("Backup completed without errors")
        
def bkp_with_rsync(source, destination):
    src = os.path.join(source, "")
    dest = os.path.join(destination, "")
    cmd = ["rsync", "-av", src, dest]
    
    process = subprocess.run(cmd, capture_output=True, text=True)
    
    if process.returncode == 0:
        write_log("Backup rsync completed without errors")
    else:
        error_msg = process.stderr.strip()
        write_log(f"rsync error {process.returncode}: {error_msg}")
    
def main():  
    os.makedirs(bkp_folder, exist_ok=True)
        
    if shutil.which("rsync"):
        bkp_with_rsync(source_folder, bkp_folder)
    else:
        bkp_with_os(source_folder, bkp_folder)
        
    try:
        subprocess.run(["sync"], check=True)
        subprocess.run(["systemctl", "stop", "mnt-bkp_disk.mount"], check=True)
        write_log("Disk succesfully unmounted.")
    except subprocess.CalledProcessError as error:
        write_log(f"Disk unmount error: {error} Possible data corruption")
        
if __name__ == "__main__":
    main()
        
