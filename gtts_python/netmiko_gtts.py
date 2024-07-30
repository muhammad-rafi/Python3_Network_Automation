from gtts import gTTS
import os
from netmiko import ConnectHandler
from ntc_templates.parse import parse_output
from pprint import pprint


# Define the network device details
device = {
    'device_type': 'cisco_ios',
    'host': 'cml-dist-rtr01',
    'port': 22,
    'username': 'admin',
    'password': 'C1sco123',
}

# Establish SSH connection to the network device
net_connect = ConnectHandler(**device)

# Define the command to retrieve interface status
show_command = 'show ip interface brief'

# Send the command and retrieve the output
command_output = net_connect.send_command(show_command)

# Close the SSH connection
net_connect.disconnect()

# Use NTC template to parse the output
parsed_command_output = parse_output(platform="cisco_ios", command=show_command, data=command_output)

# # Find down interfaces
down_interfaces = [item['intf'] for item in parsed_command_output if 'administratively down' in item['status'] ]
# pprint(down_interfaces)

# Generate the speech message
message = 'The following interfaces are administratively down: {}'.format(', '.join(down_interfaces))
print(message)

# Convert the message to speech
tts = gTTS(message, lang='en-uk', slow=False, tld='co.uk')

# Save the audio file
tts.save("output.mp3")

# Play the audio file
os.system('afplay output.mp3')
