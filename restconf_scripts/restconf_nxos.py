import requests
import json
import sys

requests.packages.urllib3.disable_warnings()

def resconf_get_nxos(host, username, password, path, port=443):
   
   try:
      headers = {
            "Accept" : "application/yang.data+json", 
            "Content-Type" : "application/yang.data+json", 
         }
      
      url = f"https://{host}:{port}/restconf/data/{path}"
      response = requests.get(url, 
                           auth=(username,password), 
                           headers=headers,
                           verify=False)

   except requests.RequestException as e:
      print(e)

   # To return response output in Python dict format
   # return response.json()

   # To return response output in JSON format
   return response.text   


def resconf_config_nxos(host, username, password, path, data, method='PUT', port=443):

   try:
      headers = {
            "Accept" : "application/yang.data+json", 
            "Content-Type" : "application/yang.data+json", 
         }
      url = f'https://{host}:{port}/restconf/data/{path}'
      response = requests.request(method, url, 
                           auth=(username,password), 
                           headers=headers,
                           data=data,
                           verify=False,
                           timeout=30)

      if response.status_code == 200 or response.status_code == 204:
         response_code = f"Content created successfully, {response.status_code} !"
         return response_code

   except requests.RequestException as e:
      print(e)


if __name__ == '__main__':

   device = {
      "host": "sbx-nxos-mgmt.cisco.com",
      "username": "admin",
      "password": "Admin_1234!",
      "port": "443",
      "path": "Cisco-NX-OS-device:System/time-items/"
   }
   
   # Get the ntp server congiruation 
   # print(resconf_get_nxos(**device))

   data = '''{
         "prov-items":{
            "NtpProvider-list":[
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
                  "name":"172.16.1.11",
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
   config  = resconf_config_nxos(device['host'], 
                                 device['username'], 
                                 device['password'], 
                                 path=device['path'], 
                                 data=data, 
                                 method='PUT')

   # print the output of the request's response
   print(config)

   # Get the updated configuration after the above change
   print(resconf_get_nxos(**device))
