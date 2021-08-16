from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException
from rich.console import Console
from rich.table import Table
from getpass import getpass
import json 

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

# This function will return the interfaces operational configs and will present the data in pretty table format
def get_interfaces(username, password, devices, port=22):

    # 'for loop' to iterate over the devices in the 'devices_list'
    for host in devices:
    
        print ('Connecting to ' + host + ' ...' )
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
            print('Connection has been established, waiting for the ouput ...')
                
            # Send the desired command and save in the output variable in 'Interfaces_dict_json'
            Interfaces_dict_json = net_connect.send_command('show interface | json-pretty')
                
            # Convert the json str object 'Interfaces_dict_json' in to the python dictionary 
            Interfaces_dict_py = json.loads(Interfaces_dict_json)
    
            # Filter the desired output from the 'Interfaces_dict_py' results  and save into 'interfaces' as list of dictionary
            interfaces = Interfaces_dict_py['TABLE_interface']['ROW_interface']
    
            # Create a table to store and set the columns with the headers
            table = Table(show_header=True, header_style="bold blue")
            columns = ['Interface', 'Description', 'State', 'Admin_Status', 'MTU_Size']
            for column in columns:
                table.add_column(column, justify='left')

            # Loop through the intefaces dictionary in the 'interfaces' output and parse the desired output into variables
            for interface in interfaces: 
                name = interface.get('interface')
                desc = interface.get('desc') or interface.get('svi_desc')  
                admin_state = interface.get('admin_state') or interface.get('svi_admin_state')
                state = interface.get('state') or interface.get('svi_line_proto')
                mtu = interface.get('eth_mtu') or interface.get('svi_mtu')

                # create a dictionary with the parse item variables as values  
                interface_dict = {
                        'Interface': name,
                        'Description': desc, 
                        'State': state,
                        'Admin_Status': admin_state,
                        'MTU_Size': mtu
                        }

                # populated the rows with the out of the variables from the interfaces
                table.add_row(*interface_dict.values())
            
            # create a console object to print the final table
            console = Console(record=True)
            print_console = console.print(table)
                
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

    # Get the list of devices from the file 
    devices = read_devices("devices.txt")
    
    # Get the login credentials
    username, password = login_credentials()
    
    # Get the interfaces output, add 'port=<kwargs>' too, if port is different than default 22
    get_interfaces(username, password, devices)
  