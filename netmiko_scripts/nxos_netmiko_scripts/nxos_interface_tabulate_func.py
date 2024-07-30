from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException
from netmiko.exceptions import AuthenticationException
from netmiko.exceptions import SSHException
from paramiko.ssh_exception import SSHException
from getpass import getpass
import json 
import time
import datetime
from tabulate import tabulate
from operator import itemgetter

time_now = datetime.datetime.now().isoformat(timespec='seconds')
print(time_now)

def login_credentials():
    """ get the devices login details from user
    """
    username = input('Enter you username: ')
    password = getpass('password: ')
    return username, password


def read_devices(devices_file):
    """ Returns list of devices from the file 
    and split them in lines
    """
    with open(devices_file) as f:
        devices_list = f.read().splitlines()
        return devices_list

def get_interfaces(username, password, devices, port=22):

    # 'for loop' to iterate over the devices in the 'devices_list'
    for host in devices:
        
        print("=" * 75)
        print('Connecting to the ' + host + ' ...' )
        print("=" * 75)
        
        device = {
            'device_type': 'cisco_nxos',
            'host': host,
            'username': username,
            'password': password,
            'secret': password,
            'port': port,
            'global_delay_factor': 20
            }
        
        # 'try and except' block which will handle the exceptions 
        try:

            # Establishing the connection with device  
            net_connect = ConnectHandler(**device)    
                
            # Printing a message on the terminal 
            print("*" * 75)
            print('Connection has been established, waiting for the ouput ...')
            print("*" * 75)
            
            # Send the desired command and save in the output variable in 'Interfaces_dict_json'
            Interfaces_dict_json = net_connect.send_command('show interface | json')
                
            # Convert the json str object 'Interfaces_dict_json' in to the python dictionary 
            Interfaces_dict_py = json.loads(Interfaces_dict_json)
    
            # Filter the desired output from the 'Interfaces_dict_py' results  and save into 'interfaces' as list of dictionary
            interfaces = Interfaces_dict_py['TABLE_interface']['ROW_interface']   
            
            # Create an empty list, which we will use for the tabulated function 
            interface_list = list()
    
            # Loop through the list of dictionary of 'interfaces' and parse the desired output into variables 
            for interface in interfaces: 
                name = interface.get('interface')
                desc = interface.get('desc') or interface.get('svi_desc')  
                admin_state = interface.get('admin_state') or interface.get('svi_admin_state')
                state = interface.get('state') or interface.get('svi_line_proto')
                mtu = interface.get('eth_mtu') or interface.get('svi_mtu')
                speed = interface.get('eth_speed') 
                mac = interface.get('eth_bia_addr') or interface.get('svi_mac')
                
                # create a list of dictrionary with the help of above variables 
                interface_dict = {
                        #'HOSTNAME': device['host'],
                        'INTERFACE': name,
                        'DESCRIPTION': desc, 
                        'STATE': state,
                        'ADMIN STATE': admin_state,
                        'MTU SIZE': mtu,
                        'SPEED': speed,
                        'MAC ADDRESS': mac
                        }
                
                # append the previously created list 'interface_list'
                interface_list.append(interface_dict)
            
            # print the output of 'interface_list' in nicely formatted table and sorted with 'MTU_Size'
            print(tabulate(sorted(interface_list, key=lambda item: item.get("MTU SIZE")), headers="keys"))
            print('\n')
            # print(tabulate(sorted(interface_list, key=itemgetter("MTU SIZE")), headers="keys"))


        # except block will catch exceptions during the execution of this script
        except (KeyboardInterrupt):
            print ('[KeyboardInterrupt ERROR]: User has closed the connection')
            continue 
    
        except (AuthenticationException):
            print ('[Authentication ERROR]: Authentication Failed for ' + host)
            continue 
        
        except (NetMikoTimeoutException):
            print ('[Timeout ERROR]: Unable to connect to ' + host + '. The device timed out.' )
            continue
        
        except (SSHException):
            print ('[SSHException ERROR]: Please check if SSH is enabled for ' + host)
            continue 
        
        except (EOFError):
            print ('[EOF ERROR]: End of File whilte attempting device: ' + host)
            continue
        
        except (ValueError): 
            print ('[ValueError]: Unsupported device_type for ' + host)
            continue
            
        except FileNotFoundError:
            print("Error: FileNotFoundError, please check the file path")
            continue
        
        except Exception as e:
            print(e) 


if __name__ == "__main__":
    
    # start time of the script
    start_time = datetime.datetime.now()
    
    # Read the devices from the 'devices.txt' file, please comment out if you like to use the list of devices 
    # devices = read_devices("devices.txt")

    # Get the login credentials
    username, password = login_credentials()
    
    # please comment out this variable if you are using 'devices.txt' file to read the device from
    devices = ['sbx-nxos-mgmt.cisco.com']
    
    # Get the interfaces output in a nicely formatted table, note: 'port' is optional unless different than the default '22' 
    get_interfaces(username, password, devices, port=8181)
    
    # end time of the script 
    end_time = datetime.datetime.now()
    
    # Print the total time it takes to execute the script 
    print("Total time: {}".format(end_time - start_time))
    
    
