import requests
import json
import sys

requests.packages.urllib3.disable_warnings()

data = '''{
      "prov-items":{
         "NtpProvider-list":[
            {
               "name":"172.16.1.11",
               "keyId":"1",
               "maxPoll":"6",
               "minPoll":"4",
               "preferred":"false",
               "provT":"peer",
               "vrf":"management"
            },
            {
               "name":"172.16.1.12",
               "keyId":"1",
               "maxPoll":"6",
               "minPoll":"4",
               "preferred":"false",
               "provT":"peer",
               "vrf":"management"
            },
            {
               "name":"172.16.0.1",
               "maxPoll":"6",
               "minPoll":"4",
               "preferred":"false",
               "provT":"server"
            }
         ]
      }
   }
   '''

device = {
   "host": "sbx-nxos-mgmt.cisco.com",
   "username": "admin",
   "password": "Admin_1234!",
   "port": "443",
   "path": "Cisco-NX-OS-device:System/time-items/"
}

headers = {
      "Accept" : "application/yang.data+json", 
      "Content-Type" : "application/yang.data+json", 
   }

url = f"https://{device['host']}:{device['port']}/restconf/data/{device['path']}"

response = requests.request('PUT', url, 
                     auth=(device['username'],device['password']), 
                     headers=headers,
                     data=data,
                     verify=False,
                     timeout=30)

if response.status_code == 200 or response.status_code == 204:
   print(f"Content created successfully, {response.status_code} !")

elif response.status_code == 400:
   print('HTTP Error [400] Bad Request, please check the payload!')

elif response.status_code == 500:
   print('HTTP Error [500] Internal Server Error!')

elif response.status_code == 405:
   print('HTTP Error [405] This request is not allowed!')

else:
   print(responsestatus_code)

