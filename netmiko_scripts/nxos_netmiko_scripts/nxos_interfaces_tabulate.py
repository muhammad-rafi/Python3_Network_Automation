from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException
from netmiko.exceptions import AuthenticationException
from netmiko.exceptions import SSHException
from paramiko.ssh_exception import SSHException
from getpass import getpass
import json 
import csv 
from tabulate import tabulate
from operator import itemgetter
from colorama import Fore, Style, init
from termcolor import colored

init(convert=True)

# List of devices 
# devices = ['sbx-nxos-mgmt.cisco.com']

def read_devices(devices_file):
    """ Returns list of devices from the file 
    and split them in lines
    """
    with open(devices_file) as f:
        devices_list = f.read().splitlines()
        return devices_list

devices = read_devices('devices.txt')

#print(devices) 

# List of commands
commands = ('show interface | json-pretty')

# Ask user to enter the username 
username=input('username: ')

# Ask user to enter the password  
password=getpass('password ')

# 'for loop' to iterate over the devices mentioned in the 'devices'
for host in devices:

    print ('Connecting to ' + host + ' ...' )
    device = {
        'device_type': 'cisco_nxos',
        'host': host,
        'username': username,
        'password': password,
        'secret': password,
        'port': '22'
        }
    
    try:
        # Establishing the connection with device  
        net_connect = ConnectHandler(**device)    
        
        # Printing a message on the terminal 
        print('Connection has been established, waiting for the ouput ...')
        
        # Send the desired command and save in the output variable 
        Interfaces_dict_json = net_connect.send_command(commands)
        
        # Conver the str object (Interfaces_dict_json) in to the python dictionary 
        Interfaces_dict_py = json.loads(Interfaces_dict_json)

        # Filter the output of the above Interfaces_dict_py 
        interfaces = Interfaces_dict_py['TABLE_interface']['ROW_interface']
        # print(interfaces)

        interface_list = list()

        # Loop through the list of dictionary of 'interfaces' and parse the desired output into variables 
        for interface in interfaces: 
            name = interface.get('interface')
            desc = interface.get('desc') or interface.get('svi_desc')  
            admin_state = interface.get('admin_state') or interface.get('svi_admin_state')
            state = interface.get('state') or interface.get('svi_line_proto')
            mtu = interface.get('eth_mtu') or interface.get('svi_mtu')

            # create a list of dictrionary with the help of above data
            interface_dict = {
                    'HOSTNAME': device['host'],
                    'INTERFACE': name,
                    'DESCRIPTION': desc, 
                    'STATE': state,
                    'ADMIN STATE': admin_state,
                    'MTU SIZE': mtu
                    }
            
            interface_list.append(interface_dict)
        
        # print the output of interface_list in nicely formatted table 
        #print(interface_list)
        print(tabulate(sorted(interface_list, key=lambda item: item.get("MTU SIZE")), headers="keys"))

    # except block will catch exceptions during the execution of this script
    except (KeyboardInterrupt):
        print (colored('[KeyboardInterrupt ERROR]: User has closed the connection', 'red'))
        continue 
    
    except (AuthenticationException) as e:
        print(colored('[Authentication ERROR]: Authentication Failed for ' + host, 'red'))
        continue 
    
    except (NetMikoTimeoutException):
        print(colored('[Timeout ERROR]: Unable to connect to ' + host + '. The device timed out.', 'red'))
        continue
    
    except (SSHException):
        print(colored('[SSHException ERROR]: Please check if SSH is enabled for ' + host, 'red'))
        continue 
    
    except (EOFError):
        print(colored('[EOF ERROR]: End of File whilte attempting device: ' + host, 'red'))
        continue
    
    except (ValueError): 
        print(colored('[ValueError]: Unsupported device_type for ' + host, 'red'))
        continue
        
    except FileNotFoundError:
        print(colored("Error: FileNotFoundError, please check the file path", 'red'))
        continue
    
    except Exception as e:
        print(colored(e, 'red'))
        