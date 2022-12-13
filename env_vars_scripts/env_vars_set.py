import os 
import ast
import json
from rich import print 

# Set Environment Variables for username and password 
os.environ["USERNAME"] = "super-mario"
os.environ["PASSWORD"] = "4Sup3rs3cReT"

# TO FETCH THE ENVIRONMENT VARIABLES SET ABOVE 

## FIRST METHOD 
username = os.environ["USERNAME"]
password = os.environ["PASSWORD"]

print('\nGetting Environment Variables via os.environ["USERNAME"]')
print(f'username: {username}\npassword: {password}\n')

## SECOND METHOD 
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

print('Getting Environment Variables via os.environ.get("USERNAME")')
print(f'username: {username}\npassword: {password}\n')

## THIRD METHOD 
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

print('Getting Environment Variables via os.getenv("USERNAME")')
print(f'username: {username}\npassword: {password}\n')

#--------------------------------------------------------------------------------------------#
# Set an Integer type environment variable as string and then convert string to an integer
os.environ["PORT"] = "443"

port_no = int(os.environ["PORT"])
print(f'port number: {port_no} type: {type(port_no)}', end='\n'*2)

print(int(os.environ.get("PORT")), type(int(os.environ.get("PORT"))), end='\n'*2)

print(int(os.getenv("PORT")), type(int(os.getenv("PORT"))), end='\n'*2)

#--------------------------------------------------------------------------------------------#
# Set a Float type environment variable as string and then convert string to float 
os.environ["PI_VALUE"] = "3.14"

value_of_pie = float(os.environ["PI_VALUE"])
print(f'Value of Pi: {value_of_pie} type: {type(value_of_pie)}', end='\n'*2)

#--------------------------------------------------------------------------------------------#
# Set a Boolean type environment variable as string and then convert string to boolean 
os.environ["VERIFY_CERT"] = "True"

verify_cert = bool(os.environ["VERIFY_CERT"])
print(f'Verify Certificate: {verify_cert} type: {type(verify_cert)}', end='\n'*2)

#--------------------------------------------------------------------------------------------#
# Set a List type environment variable as string and then convert string to list 

os.environ["DEVICES"] = "['device1', 'device2', '10.0.0.1']"

# devices_list = ast.literal_eval(os.environ["DEVICES"])
devices_list = eval(os.environ["DEVICES"])
print(f'List of devices: {devices_list} type: {type(devices_list)}', end='\n'*2)

#--------------------------------------------------------------------------------------------#
# Set a Dict type environment variable as string and then convert string to dictionary 

os.environ["DEVICE"] = '''{"device_type": "cisco_ios",
                           "host": "core01-rtr01",
                           "username": "admin",
                           "password": "cisco",
                           "port": 22
                           }'''

device = json.loads(os.environ["DEVICE"])
# device = eval(os.environ["DEVICE"])
print(f'Device: {device} type: {type(device)}', end='\n'*2)
