#!/usr/bin/env python

import yaml
from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException
from os import rename
from os.path import isfile
import argparse

exceptions = (
    NetMikoAuthenticationException,
    NetMikoTimeoutException,
    Exception)


def shuffle(file_name, ext1, ext2):
    ext1 = f'-{ext1}'
    ext2 = f'.{ext2}'

    if isfile(f'{file_name}{ext1}'):
        if isfile(f'{file_name}{ext1}{ext2}''1'):
            if isfile(f'{file_name}{ext1}{ext2}''2'):
                if isfile(f'{file_name}{ext1}{ext2}''3'):
                    if isfile(f'{file_name}{ext1}{ext2}''4'):
                        if isfile(f'{file_name}{ext1}{ext2}''5'):
                            rename(f'{file_name}{ext1}{ext2}''2', f'{file_name}{ext1}{ext2}''1')
                            rename(f'{file_name}{ext1}{ext2}''3', f'{file_name}{ext1}{ext2}''2')
                            rename(f'{file_name}{ext1}{ext2}''4', f'{file_name}{ext1}{ext2}''3')
                            rename(f'{file_name}{ext1}{ext2}''5', f'{file_name}{ext1}{ext2}''4')
                            rename(f'{file_name}{ext1}', f'{file_name}{ext1}{ext2}''5')
                        else:
                            rename(f'{file_name}{ext1}', f'{file_name}{ext1}{ext2}''5')
                    else:
                        rename(f'{file_name}{ext1}', f'{file_name}{ext1}{ext2}''4')
                else:
                    rename(f'{file_name}{ext1}', f'{file_name}{ext1}{ext2}''3')
            else:
                rename(f'{file_name}{ext1}', f'{file_name}{ext1}{ext2}''2')
        else:
            rename(f'{file_name}{ext1}', f'{file_name}{ext1}{ext2}''1')
    open(f'{file_name}{ext1}', 'w')


def func_yml(file_path_yaml, group):
    """ Read key/value and list from a yaml file. """
    with open(file_path_yaml) as f:
        file_yaml = f.read()
    yaml_dict = yaml.load(file_yaml, Loader=yaml.FullLoader)
    return yaml_dict[group]


class Login:
    def __init__(self, var_credentials: dict, var_hosts, var_device_type):

        self.output = []

        for hosts in var_hosts:
            device = {
                'device_type': var_device_type,
                'host': hosts,
                # 'global_delay_factor': 2,
                # "read_timeout_override": 90,
                # 'banner_timeout': 20,
                'session_log': 'output_high-level.log'
            }

            try:
                device.update(var_credentials)
                net_connect = ConnectHandler(**device)
                net_connect.enable()
                self.output.append(net_connect)

            except exceptions as error:
                print(error)

    def login(self):
        return self.output


class Device(Login):
    def __init__(self, var_credentials, var_hosts, var_device_type):
        super().__init__(var_credentials, var_hosts, var_device_type)

    def save(self):
        net_connect = self.login()

        output = []
        for net in net_connect:
            try:
                display = net.save_config()
                output.append(display)
            except exceptions as error:
                print(error)

        return output

    def backup(self, folder):
        net_connect = self.login()

        var_command = 'sh run'

        output = []
        for net in net_connect:
            try:
                display = net.send_command(var_command, max_loops=1000, delay_factor=5)
                output.append(display)

                folder_file_name = f'{folder}/{net.host}'

                # shuffle
                shuffle(folder_file_name, 'confg', 'BAK')

                # copy the 'sh ver' output to a file
                for o in output:
                    with open(f'{folder_file_name}-confg', 'w') as f:
                        f.write(o)

            except exceptions as error:
                print(error)

        return output


def main():
    arg_desc = '''
This program backups Cisco IOS, NXOS and ASA using the old method (shuffling). 

e.g.
    source /venv/bin/python/activate
    python main.py -u smith -p cisco1 -e cisco1 -d cisco_ios -f pass.yml -g host_oliveiras
    
Creating the yaml file:
    
    vim pass.yml
    
    ---
    host_oliveiras:
      - 192.168.56.150
      - 192.168.56.160
      - 192.168.56.170
    
Remember:
    You don't have to chmod the file or login to the device directly.
'''

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=arg_desc)

    # parser = argparse.ArgumentParser(description=arg_desc)
    parser.add_argument('-u', '--username', help='Enter username.', type=str, required=True)
    parser.add_argument('-p', '--password', help='Enter password.', type=str, required=True)
    parser.add_argument('-e', '--enable', help='Enter enable password.', type=str, required=True)
    parser.add_argument('-d', '--device_type', help='Enter device type. e.g. cisco_ios, cisco_nxos, cisco_asa', type=str, required=True)
    parser.add_argument('-f', '--file', help='Enter file name (yaml).', type=str, required=True)
    parser.add_argument('-g', '--group', help='Enter group name.', type=str, required=True)

    args = parser.parse_args()

    args_cred = {
        'username': args.username,
        'password': args.password,
        'secret': args.enable
    }

    args_host = func_yml(args.file, args.group)

    devices = Device(args_cred, args_host, args.device_type)
    print(devices.save())
    print(devices.backup('tftp'))


if __name__ == '__main__':
    main()
