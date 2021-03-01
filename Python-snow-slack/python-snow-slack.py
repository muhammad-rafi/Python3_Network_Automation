from netmiko import ConnectHandler
from getpass import getpass
from jinja2 import Template 
from colorama import Fore, Back, Style, init
from time import sleep
from datetime import datetime
from difflib import Differ, unified_diff
from snow_change_close import change_close
import sys
import colorama
import difflib


def main():
    ''' main function to configure the vlan on the nexus switches, 
    it will also close the service now changes and send the notifications
    to the slack for work completion'''
    
    try:
        # Start time of the change 
        start_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        init(convert=True)
        init(autoreset=False)
        
        # define jinja2 files as variables 
        add_vlan_file = 'add_vlan_file.j2'
        rb_add_vlan_file = 'rb_add_vlan_file.j2'
        
        
        # open jinja2 files as f1 and f2 for config and rollback configurations respectively in read mode
        with open(add_vlan_file) as f1: 
            vlan_template = Template(f1.read(), keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
        
        with open(rb_add_vlan_file) as f2: 
            rb_vlan_template = Template(f2.read(), keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
        
        # taking devices input from user and split them by comma 
        host = input("Please enter the device name/IP (for multiple devices, seperate them by ','): ")
        devices = host.strip().split(',')
        
        # taking user input for device credentials 
        username = input("Enter your username: ")
        password = getpass("password: ")
        device_type = 'cisco_nxos'
        port= 8181
        
        # Only for testing purpose against Cisco NXOS Sandbox 
        # devices = ['sbx-nxos-mgmt.cisco.com']
        # username = 'admin'
        # password = 'Admin_1234!'
        # device_type = 'cisco_nxos'
        # port= 8181
        
        # creating empty lists, so we can append them later for multiple entries 
        vlan_ids = []
        vlan_names = []
        port_numbers = []
        
        # for loop to iterate over multiple devices 
        for device in devices:
            print(Fore.BLUE + "~" * 70)
            print(" " * 18 + " Connecting to " + device)
            print("~" * 70)
            print(Style.RESET_ALL)
            net_connect = ConnectHandler(ip=device, port=port, device_type=device_type, 
                                        username=username, password=password)
            print(Fore.GREEN + "#" * 70)
            print(Fore.GREEN + " " * 18 + " Connection has been established " + Style.RESET_ALL)
            print(Fore.GREEN + "#" * 70 + Style.RESET_ALL)
            print('\n')
        
            # While loop to repeat the user input if needed 
            while True: 
                vlan_id = input("vlan number: ")
                vlan_name = input("vlan name: ")
                print('\n')
                print('validating vlan ' + vlan_id + ' ...')
                print('\n')
                output = net_connect.send_command('show vlan id ' + vlan_id)
                
                # validating the vlan, if already exist on the device
                if 'not found' in output:
                    print(Fore.GREEN + "+" * 70)
                    print(' ' * 10  + 'vlan ' + vlan_id + ' not found!, Adding the vlan ')
                    print("+" * 70 + Style.RESET_ALL)
                    print('\n')
                    vlan_ids.append(vlan_id)
                    vlan_names.append(vlan_name)
                    print('\n')    
                    question = input("would you like to add more vlans [Y/N]: ")
                    print('\n') 
                    if question.lower() in {'', 'yes', 'y', 'ye', 'yeah'}:            
                        continue    
                    else:
                        break 
        
                elif vlan_id in output:
                    print(Fore.YELLOW + "+" * 70)
                    print(' ' * 7 + 'Warning !!! vlan ' + vlan_id + ' is already configured on ' + device)
                    print(Fore.YELLOW + "+" * 70  + Style.RESET_ALL)
                    print('\n')
                    vlan_ids.append(vlan_id)
                    vlan_names.append(vlan_name)
                    print('\n')    
                    question2 = input("would you like to add more vlans [Y/N]: ")
                    print('\n') 
                    if question2.lower() in {'', 'yes', 'y', 'ye', 'yeah'}:            
                        continue    
                    else:
                        break 
                    # sys.exit(1)
                    continue
                else:
                    break
        
            # taking user input if vlans needs to be added on the port for trunk
            add_port = input("would you like to add these vlan(s) on the trunk port ? (Y/N): ")
            if add_port.lower() in {'', 'yes', 'yeah', 'y'}:
                while True: 
                    print('\n')        
                    port_number = input("Enter the trunk port you like to add the vlan on: ")
                    port_numbers.append(port_number)
                    print('\n')
                    question = input("would you like to add more ports (Y/N): ")
                    if question.lower() in {'', 'yes', 'y', 'ye'}:
                    # if question.lower() == 'y':
                        continue    
                    else:
                        break 
        
        # convert vlan_ids list into the string
        vlan_id_str = ", ".join(vlan_ids)
        # print(vlan_id_str)
        # print(port_numbers)
        
        # zipped vlan_ids and vlan_names lists to iterate them over in jinja2 template
        vlans = zip(vlan_ids, vlan_names)
        
        # Using Jinja2 template defined above 'add_vlan_file.j2' to generate the config 
        vlan_config_j2 = vlan_template.render(
                                        vlans=vlans, 
                                        port_numbers=port_numbers,
                                        vlan_id_str=vlan_id_str
                                        )
        
        print('\n' + Fore.LIGHTGREEN_EX + "#" * 70)
        print(vlan_config_j2)
        print(Fore.LIGHTGREEN_EX + "#" * 70 + Style.RESET_ALL + '\n')
        
        # asking user if pre-checks is required and performing pre-checks if answered yes
        pre_output = ''
        pre_sh_vlan_id = ''
        pre_checks = input('would you like to do the pre-checks? (Y/N): ')
        if pre_checks.lower() in {'', 'yes', 'y', 'ye'}:
            for vlan_id in vlan_ids:
                pre_sh_vlan_id = net_connect.send_command(f'show vlan id {vlan_id}')
                sh_span_vlan = net_connect.send_command(f'show span vlan {vlan_id}')
                print("~" * 90)
                print(pre_sh_vlan_id)
                print("~" * 90)
                print(sh_span_vlan)
                print("~" * 90)
            for port_number in port_numbers:
                output = net_connect.send_command(f'show run interface {port_number}')
                print(output)
                pre_output += output
        else: 
            pass

        # asking user if presented config need to be sent to the device 
        send_config = input('would you like to send this config to the device? (Y/N): ')
        if send_config.lower() in {'', 'yes', 'y', 'ye'}:
            output = net_connect.send_config_set(vlan_config_j2.splitlines())
            devices_list = ', '.join(str(d) for d in devices)
            print("\n")
            print("+" * 70)
            print(' ' * 20 + Fore.GREEN + 'vlan(s) now configured!' + Style.RESET_ALL)
            print("+" * 70)
            print("\n")
        else: 
            pass
        
        # asking user if post-checks is required and performing post-checks if answered yes
        post_output = ''
        post_sh_vlan_id = ''
        verify_config = input('would you like to do the post-checks? (Y/N): ')
        if verify_config.lower() in {'', 'yes', 'y', 'ye'}:
            for vlan_id in vlan_ids:
                post_sh_vlan_id = net_connect.send_command(f'show vlan id {vlan_id}')
                sh_span_vlan = net_connect.send_command(f'show span vlan {vlan_id}')
                print("~" * 90)
                print(post_sh_vlan_id)
                print("~" * 90)
                print(sh_span_vlan)
                print("~" * 90)
            for port_number in port_numbers:
                output = net_connect.send_command(f'show run interface {port_number}')
                print(output)
                post_output += output
        else: 
            pass 
        
        # Checking the difference in the config against pre config and post config 
        def color_diff(diff):
            for line in diff:
                if line.startswith('+'):
                    yield Fore.GREEN + line + Fore.RESET
                    #print(Fore.GREEN + line + Fore.RESET)
                elif line.startswith('-'):
                    yield Fore.RED + line + Fore.RESET
                    #print(Fore.RED + line + Fore.RESET)            
                elif line.startswith('^'):
                    yield Fore.BLUE + line + Fore.RESET
                    #print(Fore.BLUE + line + Fore.RESET)
                else:
                    yield line
                    #print(line)
        
        config_compare = input('would you like to do config diff? (Y/N): ')
        if config_compare.lower() in {'', 'yes', 'y', 'ye'}:
            #comparing the output of the configuration using unified_diff from difflib 
            print('#' *90)
            print('PRE and POST config diff') 
            print('#' *90 + '\n')
            for lines in difflib.unified_diff(pre_output.splitlines(), post_output.splitlines(), lineterm=''):
                diff_lines = color_diff(lines)
                print(''.join(diff_lines))
            print('#' *90)
        else: 
            pass 
        
        # End time of the change 
        end_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Close the change ticket via service now APIs 
        snow_change_close = input('would you like to close this change? (Y/N): ')
        if snow_change_close.lower() in {'', 'yes', 'y', 'ye'}:
            change_number = (input('please enter the change number: ')).strip()
            print(Fore.YELLOW)
            print(f'Please wait, closing the change {change_number } ....')
            print(Style.RESET_ALL)
            
            snow_change = change_close(start_time, end_time, change_number)    
            
            if snow_change == 200:
                print('\n' + Fore.GREEN + "*" * 10 + ' ' + change_number + ' has been closed !' + ' ' + "*" * 10 + Style.RESET_ALL + '\n')
            else: 
                print(f'error closing the change with the http code {snow_change}') 
        else:
            print(Fore.GREEN + "+" * 70)
            print(' ' * 20 + ' Exiting the script ... ')
            print("+" * 70  + Style.RESET_ALL)
            sys.exit(1)
        
        # Rollback the config configuration for the clean up
        rb_vlan_config_j2 = rb_vlan_template.render(
                                        vlan_ids=vlan_ids, 
                                        port_numbers=port_numbers,
                                        vlan_id_str=vlan_id_str
                                        )
                                        
        rollback_config = input('would you like to rollback this changes? (Y/N): ')
        if rollback_config.lower() == 'y':
            print('\n')
            print(Fore.LIGHTRED_EX + "#" * 70)
            print(rb_vlan_config_j2)
            print(Fore.LIGHTRED_EX + "#" * 70 + Style.RESET_ALL)
            print('\n')
            rollback_confirm = input('please check and confirm and proceed with the rollback back? (Y/N): ')
            print('\n')
            if rollback_confirm.lower() == 'y':
                rollback = net_connect.send_config_set(rb_vlan_config_j2.splitlines())
                print("\n")
                print("+" * 70)
                print(' ' * 20 + Fore.GREEN + 'Changes have been reverted!' + Style.RESET_ALL)
                print("+" * 70)
                print("\n")
            else: 
                print(Fore.GREEN + "+" * 70)
                print(' ' * 20 + ' Exiting the script ... ')
                print("+" * 70  + Style.RESET_ALL)
                sys.exit(1)
        else: 
            print(Fore.GREEN + "+" * 70)
            print(' ' * 20 + ' Exiting the script ... ')
            print("+" * 70  + Style.RESET_ALL)
            sys.exit(1)
    
    except Exception as e:
        print(Fore.RED + "~" * 10 + str(e) + "~" * 10 + Style.RESET_ALL)

if __name__ == '__main__':
    main()