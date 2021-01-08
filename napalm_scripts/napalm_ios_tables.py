from napalm import get_network_driver
from tabulate import tabulate
from operator import itemgetter
from getpass import getpass
import time 
import datetime
import json


''' please ignore this as this is for testing purpose to create this class as an altervative way '''
#class IosTables:
#
#    username = input('Enter you username: ')
#    password = getpass('password: ')
#
#    def __init__(self, device, port=22):    
#        self.device = device
#        self.port = port
#        driver = get_network_driver('ios')
#        self.session = driver(device, self.username, self.password, optional_args={'port':port})
#        print(f'Connecting to {self.device} ...')
#        time.sleep(2)
        
class IosTables:
    
    def __init__(self, device, username, password, port=22):
        self.device = device
        self.username = username 
        self.password = password 
        self.port = port
        driver = get_network_driver('ios')
        self.session = driver(device, username, password, optional_args={'port':port})

    def device_connect(self):
        self.session.open()


    def device_disconnect(self):
        self.session.close()


    def facts_table(self):
        print("=" * 75 + f'\nConnecting with {self.device} ...\n' + "=" * 75)
        time.sleep(2)
        
        try:
            self.device_connect()
            print(f'Connection has been established ...\n' + "=" * 75 + '\n')
            time.sleep(2)
            print("*" * 75 + f'\nGetting the {self.device} facts table\n' + "*" * 75 )
            
            facts_table = self.session.get_facts()
            
            facts_table_list = list()
            
            facts_dict = {
                'HOSTNAME': facts_table['hostname'],
                'MODEL': facts_table['model'],
                'VENDOR': facts_table['vendor'],
                'OS VERSION': facts_table['os_version'].split(',')[1],
                'SERIAL NUMBER': facts_table['serial_number'], 
                'UPTIME': facts_table['uptime']
                }
            
            facts_table_list.append(facts_dict)
            
            self.device_disconnect()
            return tabulate(sorted(facts_table_list, key=lambda item: item.get("HOSTNAME")), headers="keys")
            
        except Exception as e:
            print(e)
    
    
    def arp_table(self, vrf=''):
        print('\n' + "*" * 75 + f'\nGetting the {self.device} arp table\n' + "*" * 75 + '\n')
        
        try: 
            self.device_connect()
            arp_table = self.session.get_arp_table(vrf='')
            
            arp_table_list = list()
            
            for arp in arp_table:
                
                if arp['age'] == -1:
                    age = '-'
                else:
                    age = int(arp['age'])
                    
                arp_dict = {
                    'IP ADDRESS': arp['ip'], 
                    'MAC ADDRESS': arp['mac'],
                    'AGE (Min)': age,
                    'INTERFACE': arp['interface']
                    }
                    
                arp_table_list.append(arp_dict)
            
            self.device_disconnect()
            return tabulate(sorted(arp_table_list, key=lambda item: item.get("INTERFACE")), headers="keys")
        
        except Exception as e:
            print(e) 


    def interfaces_table(self): 
            
        print('\n' + "*" * 75 + f'\nGetting the {self.device} Interfaces table\n' + "*" * 75 + '\n')
        
        try: 
            self.device_connect()
            interfaces = self.session.get_interfaces()
            
            intf_table = [['INTERFACES', 'DESCRIPTION', 'STATUS', 'ADMIN STATUS', 'MTU SIZE', 'MAC ADDRESS']]
            
            for interface in interfaces:
            
                desciption = interfaces[interface]['description']
                mtu = interfaces[interface]['mtu']
                mac_address = interfaces[interface]['mac_address']
            
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
                
                intf_table.append([interface, desciption, status, admin_status, mtu, mac_address])
            
            self.device_disconnect()
            return print(tabulate(intf_table, headers='firstrow'))
            
        except Exception as e:
            print(e)


    def vrf_table(self, vrf=''):

        print('\n' + "*" * 75 + f'\nGetting the {self.device} VRF table\n' + "*" * 75 + '\n')
        
        try: 
            self.device_connect()
            vrfs = self.session.get_network_instances(name=vrf)
            
            vrf_table_list = list()
            
            for vrf in vrfs:
                vrf_name = vrfs[vrf]['name']
                vrf_type = vrfs[vrf]['type']
                vrf_rd = vrfs[vrf]['state']['route_distinguisher']
                
                vrf_table_dict = {
                    'VRF NAME': vrf_name,
                    'TYPE': vrf_type,
                    'RD': vrf_rd,
                    }
                    
                vrf_table_list.append(vrf_table_dict)
            
            print(tabulate(sorted(vrf_table_list, key=lambda item: item.get("TYPE")), headers="keys"))
            
            self.device_disconnect()
            
        except Exception as e:
            print(e)

if __name__ == '__main__':
    
    # please ignore this as this is for testing purpose to call the testing class above
    # device = IosTables("ios-xe-mgmt.cisco.com", port=8181)
    
    # Use this method if you don't want to keep your login credentials in the script 
    # username = input('Enter you username: ')
    # password = getpass('password: ')
    # device = IosTables("ios-xe-mgmt.cisco.com", username, password, port=8181)
    
    # Use this method to instantiate an object with one line, be mindful your password be kept unencrypted in this script, port argument is optional here, only required if port is different than '22' 
    device = IosTables("ios-xe-mgmt.cisco.com", "developer", "C1sco12345", port=8181)
    
    # Printing the device facts in a table format 
    print(device.facts_table())
    
    # printing the arp table for all vrfs, for specific vrf, please place the vrf name in argument e.g. vrf='management'
    print(device.arp_table(vrf=''))
    
    # printing the interfaces in a table format 
    print(device.interfaces_table())
    
    # printing the list of vrfs along with their type and RD values 
    #print(device.vrf_table(vrf=''))