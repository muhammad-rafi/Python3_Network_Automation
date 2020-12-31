from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException
from getpass import getpass
from termcolor import colored
from colorama import Fore, Style, init
import json 
import csv 

init(convert=True)

# List of devices 
#devices = ['sbx-nxos-mgmt.cisco.com']

def read_devices(devices_file):
    """ Returns list of devices from the file 
    and split them in lines
    """
    with open(devices_file) as f:
        devices_list = f.read().splitlines()
        return devices_list

devices = read_devices('devices.txt')

# List of commands
commands = ('show interface | json-pretty')

# Ask user to enter the username 
username=input('username: ')

# Ask user to enter the password  
password=getpass('password ')

# 'for loop' to iterate over the devices mentioned in the 'devices'
for host in devices:

    print(Fore.GREEN + "=" * 75)
    print(Fore.BLUE + 'Connecting to ' + host + ' ...')
    print(Fore.GREEN + "=" * 75)
    device = {
        'device_type': 'cisco_nxos',
        'host': host,
        'username': username,
        'password': password,
        'secret': password,
        'port': '22'
        #'global_delay_factor': 20
        }
    
    try:

        # Establishing the connection with device  
        net_connect = ConnectHandler(**device)    
            
        # Printing a message on the terminal 
        print(Fore.GREEN + "*" * 75)
        print(Fore.BLUE + 'Connection has been established, saving the ouput ...')
        print(Fore.GREEN + "*" * 75)
        
        # Send the desired command and save in the output variable 
        Interfaces_dict_json = net_connect.send_command(commands)
            
        # Conver the str object (Interfaces_dict_json) in to the python dictionary 
        Interfaces_dict_py = json.loads(Interfaces_dict_json)

        # Filter the output of the above Interfaces_dict_py 
        interfaces = Interfaces_dict_py['TABLE_interface']['ROW_interface']

        # creata a csv file with the same name as the hostname/IP of device connected 
        with open(host + '.csv', 'w', newline='') as f:
            #fieldnames = ['Interface', 'Description', 'State', 'Admin_Status', 'MTU_Size']
            fieldnames = ['HOSTNAME', 'INTERFACE', 'DESCRIPTION', 'STATE','ADMIN STATE', 'MTU SIZE']
            
            csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
            csv_writer.writeheader()

            # Loop through the intefaces dictionary in the 'interfaces' output and parse the desired output
            for interface in interfaces: 
                name = interface.get('interface')
                
                # Validate all the required dictionary exists in the interface variable dictionary 
                if 'desc' or 'svi_desc' in interface:
                    desc = interface.get('desc') or interface.get('svi_desc')  

                if 'admin_state' or 'svi_admin_state' in interface:
                    admin_state = interface.get('admin_state') or interface.get('svi_admin_state')

                if 'state' or 'svi_line_proto' in interface:
                    state = interface.get('state') or interface.get('svi_line_proto')

                if 'eth_mtu' or 'svi_mtu' in interface:
                    mtu = interface.get('eth_mtu') or interface.get('svi_mtu')

                # create a dictionary with the parse item above 
                interface_dict = {
                        'HOSTNAME': device['host'],
                        'INTERFACE': name,
                        'DESCRIPTION': desc, 
                        'STATE': state,
                        'ADMIN STATE': admin_state,
                        'MTU SIZE': mtu
                        }
                
                # print(interface_dict)

                # pass the 'interface_dict' as an argument to the csv writerrow() function
                csv_writer.writerow(interface_dict)
        f.close()
        print(colored('Completed, ' + host + '.csv has been saved.', 'green'))
        
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
        print(Fore.RED + "~" * 10 + str(e) + "~" * 10)
        