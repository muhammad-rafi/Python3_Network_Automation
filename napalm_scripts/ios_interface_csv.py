from napalm import get_network_driver
from getpass import getpass
from colorama import Fore, Style, init
import json 
import csv 
import time
import datetime

# Required on windows to show the colors in the terminal 
init(convert=True)

# Read the devices from the file 
def read_devices(devices_file):
    """ Returns list of devices from the file 
    and split them in lines
    """
    with open(devices_file) as f:
        devices_list = f.read().splitlines()
        return devices_list


def login_credentials():
    """ get the devices login details from user
    """
    username = input('Enter you username: ')
    password = getpass('password: ')
    return username, password


def get_interfaces(username, password, devices, port=22):
    """ Return the interfaces statistics or layer2 information in a table format """
    
    # Loop through list of devices mentioned above and fetch interfaces L2 infromation 
    for device in devices:
        print(Fore.GREEN + "*" * 30 + " " * 4 + "connecting to " + device + " " * 4 + "*" * 30 + Style.RESET_ALL)

        try:
            
            # Setting the network driver for naplam to detect the device type
            driver = get_network_driver('ios')
            
            # Building a network connnection to the device 
            device_conn = driver(device, username, password, optional_args={'port':port})
            device_conn.open()
            print("Successfully connected! waiting for the output ..." + Style.RESET_ALL)
            
            # Run the napalm "get_interfaces" module to get the fact and interface information
            device_facts = device_conn.get_facts()
            interfaces = device_conn.get_interfaces()
            #print(interfaces)
            # print(type(interfaces))
            
            # Dump the output in json-pretty format for the readability 
            # interfaces_json = json.dumps(interfaces, indent=4)
            # print(interfaces_json)
            # print(type(interfaces_json))
            
            # close the connectino to the device 
            device_conn.close()
        
            # creata a csv file with the same name as the hostname/IP of device connected 
            with open(device + '.csv', 'w', newline='') as f:
                #fieldnames = ['HOSTNAME', 'INTERFACE', 'DESCRIPTION', 'STATUS','ADMIN STATUS', 'MTU SIZE']
                fieldnames = ['INTERFACE', 'DESCRIPTION', 'STATUS','ADMIN STATUS', 'MTU SIZE', 'MAC ADDRESS']
                    
                csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
                csv_writer.writeheader()    
            
                for interface in interfaces:
                
                    if interfaces[interface]['is_up'] == True:
                        status = 'up'
                    elif interfaces[interface]['is_up'] == False:
                        status = 'down'
                    else: 
                        status = interfaces[interface]['is_up']
                
                    if interfaces[interface]['is_enabled'] == True:
                        admin_status = 'up'
                    elif interfaces[interface]['is_enabled'] == False:
                        admin_status = 'down'
                    else: 
                        admin_status = interfaces[interface]['is_enabled']
                    
                    interface_dict = {
                            #'HOSTNAME': device_facts['hostname'],
                            'INTERFACE': interface,
                            'DESCRIPTION': interfaces[interface]['description'], 
                            'STATUS': status,
                            'ADMIN STATUS': admin_status,
                            'MTU SIZE': interfaces[interface]['mtu'],
                            'MAC ADDRESS': interfaces[interface]['mac_address']
                            }
        
        
                    # print(interface_dict)
                    
                    # writing rows in the csv file opened above with the help of 'interface_dict' output 
                    csv_writer.writerow(interface_dict)
            
            time.sleep(1)
            print(f'{device}.csv has been saved')
            print(Fore.BLUE + "\n \t"+ "*" * 30 + " " * 4 + "Completed ! " + " " * 4 + "*" * 30 + Style.RESET_ALL)
            
        except Exception as e:
            print(Fore.RED + str(e) + Style.RESET_ALL)

if __name__ == '__main__':

    # start time of the script
    start_time = datetime.datetime.now()
    
    # Get the login credentials
    username, password = login_credentials()

    # Read the devices from the 'devices.txt' file, please comment out if you like to use the list of devices 
    #devices = read_devices("devices.txt")
    
    # please comment out this variable if you are using 'devices.txt' file to read the device from
    devices = ['ios-xe-mgmt.cisco.com']
    
    # Get the interfaces output and save in a csv file, note: 'port' is optional unless different than the default '22' 
    get_interfaces(username, password, devices, port=8181)
    
    # end time of the script 
    end_time = datetime.datetime.now()
    
    # Print the total time it takes to execute the script 
    print("Total time: {}".format(end_time - start_time))
    