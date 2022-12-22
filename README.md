# legacy_backup

This program backups Cisco IOS, NXOS and ASA using the old method (shuffling). 

e.g.
source /venv/bin/python/activate
python main.py -u developer -p C1sco12345 -e C1sco12345 -f hosts.yml

Creating the yaml file:

vim hosts.yml (you can give any name, as long as it is a yaml format.)

---
host:
  - sandbox-iosxe-recomm-1.cisco.com
  - sandbox-iosxe-latest-1.cisco.com

Remember:
    You don't have to shuffle the file.
    You don't have to chmod the file.
    You don't have to login to the device directly.