#!/usr/bin/env python

import yaml
from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException
from os import rename
from os.path import isfile
import argparse
from socket import getfqdn

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


def func_args(folder, remove_domain_name=''):
    arg_desc = '''
    This program backups Cisco IOS, NXOS and ASA using. 

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
    '''

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=arg_desc)
    parser.add_argument('-u', '--username', help='Enter username.', type=str, required=True)
    parser.add_argument('-p', '--password', help='Enter password.', type=str, required=True)
    parser.add_argument('-e', '--enable', help='Enter enable password.', type=str, required=True)
    parser.add_argument('-f', '--file', help='Enter config file name (yml).', type=str, required=True)
    args = parser.parse_args()
    args_cred = {'username': args.username, 'password': args.password, 'secret': args.enable}
    host = func_yml(args.file, 'host')
    parameters = func_yml(args.file, 'parameters')
    task = Device(args_cred, host, parameters.get('device_type'))
    task.backup(folder, remove_domain_name)


def func_input(folder, remove_domain_name=''):
    username = input('Enter the username: ')
    password = input('Enter the password: ')
    secret = input('Enter the enable password: ')
    config_file = input('Enter the config file name (yml): ')

    cred = {
        'username': username,
        'password': password,
        'secret': secret
    }
    host = func_yml(config_file, 'host')
    parameters = func_yml(config_file, 'parameters')
    task = Device(cred, host, parameters.get('device_type'))
    task.backup(parameters.get(folder), remove_domain_name)


def func_start_here(folder, remove_domain_name=''):
    cred = func_yml('start_here.yml', 'cred')
    host = func_yml('start_here.yml', 'host')
    parameters = func_yml('start_here.yml', 'parameters')
    task = Device(cred, host, parameters.get('device_type'))
    task.backup(parameters.get(folder), remove_domain_name)


class Login:
    def __init__(self, var_credentials: dict, var_hosts, var_device_type):

        # remove the duplication and get fqdn
        remove_duplicate_hosts = [getfqdn(x) for x in set(var_hosts)]
        remove_duplicate_hosts = set(remove_duplicate_hosts)

        self.output = []

        for hosts in remove_duplicate_hosts:
            device = {
                'device_type': var_device_type,
                'host': hosts,
                # 'global_delay_factor': 2,
                # "read_timeout_override": 90,
                # 'banner_timeout': 20,
                # 'session_log': 'output_high-level.log'
            }

            try:
                device.update(var_credentials)
                net_connect = ConnectHandler(**device)
                net_connect.enable()
                self.output.append(net_connect)

            except exceptions:
                print(f'{hosts}: failed')

    def login(self):
        return self.output


class Device(Login):
    def __init__(self, var_credentials, var_hosts, var_device_type):
        super().__init__(var_credentials, var_hosts, var_device_type)

    def backup(self, folder, remove_domain_name=''):
        net_connect = self.login()

        var_command = 'sh run'

        output = []
        for net in net_connect:
            try:
                net.save_config()
                display = net.send_command(var_command, max_loops=1000, delay_factor=5)
                output.append(display)

                remove_domain_name_ucl = net.host.replace(remove_domain_name, '')

                folder_file_name = f'{folder}/{remove_domain_name_ucl}'

                # shuffle
                shuffle(folder_file_name, 'confg', 'BAK')

                # copy the 'sh ver' output to a file
                for o in output:
                    with open(f'{folder_file_name}-confg', 'w') as f:
                        f.write(o)

                print(f'{net.host}: success')

            except exceptions as error:
                print(error)

        return output


def main():
    # Use Command-Line Arguments
    # func_args('tftp', '.xxx.ac.uk')

    # Use Prompt the User for Input
    # func_input('folder', '.xxx.ac.uk')

    # Use The start_here.yml File
    func_start_here('folder', '.xxx.ac.uk')


if __name__ == '__main__':
    main()
