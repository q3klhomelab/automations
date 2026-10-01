# Constructie script backup automat

1. **Scriu scriptul de backup in:**

`/usr/bin/python3 /root/backup_script.py`

2. **Aflu calea dispozitivului:**

`lsblk -f
ls -l /dev/disk/by-uuid/`

am gasit: `/dev/sda1`

3. **Interoghez udev pentru variabile legate de disk:**

`udevadm info --query=property --name=/dev/sda1`

si extrag:

```ini
DEVTYPE=partition
ID_FS_TYPE=ext4
ID_SERIAL=VBOX_HARDDISK_VBc2ccfaba-bd22448d
ID_FS_UUID=c53628df-d208-4d05-9014-0b10b3b409f7
```

4. **In fisierul** `/etc/udev/rules.d/99-backup-hdd.rules` **scriu:**

```sh
ACTION=="add", SUBSYSTEM=="block", ENV{DEVTYPE}=="partition", ENV{ID_FS_UUID}=="c53628df-d208-4d05-9014-0b10b3b409f7", TAG+="systemd", ENV{SYSTEMD_WANTS}="mnt-bkp_disk.mount backup-python.service"
```

5. **Reincarc setarile** `udev`:

`sudo udevadm control --reload-rules`

6. **Simulez conectarea fizica ca sa testez regula:**

`sudo udevadm trigger --action=add /dev/sda1`

7. **Deschid un alt terminal si rulez:**

`sudo journalctl -f`

inainte de simularea conectarii fizice ca sa vad eventuale erori

8. **Creez** `/etc/systemd/system/backup-python.service` **si in el pun:**

```ini
[Unit]
Description=Serviciu Automat Backup Python
Wants=mnt-bkp_disk.mount
Requires=mnt-bkp_disk.mount
After=mnt-bkp_disk.mount

[Service]
Type=oneshot
User=root
ExecStart=/usr/bin/python3 /root/backup_script.py

[Install]
WantedBy=multi-user.target
```

9. **Creez** `/mnt/bkp_disk`

10. **Creez fisierul** `/etc/systemd/system/mnt-bkp_disk.mount` **si in el pun:**
```ini
[Unit]
Description=Montare automata HDD Backup Extern

[Mount]
What=/dev/disk/by-uuid/c53628df-d208-4d05-9014-0b10b3b409f7
Where=/mnt/bkp_disk
Type=ext4
Options=defaults,nofail,noatime

[Install]
WantedBy=multi-user.target
```

11. **Rulez:**

```bash
sudo systemctl daemon-reload
sudo udevadm control --reload-rules
```

12. **Testez procesul:**

`sudo blockdev --rereadpt /dev/sda`


## script Python de test:
```python
from datetime import datetime

log_file = "/tmp/bkp_test.log"

with open(log_file, "a") as file:
    file.write(f"{datetime.now()} Automatizarea functioneaza\n")

print("Test reusit)
```