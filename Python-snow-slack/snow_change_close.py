import requests
import json 
from getpass import getpass
from datetime import datetime
from slack_sdk import WebClient
import os 
# python-dotenv
from dotenv import load_dotenv
#import dotenv

#dotenv.load_dotenv()
load_dotenv()

def change_close(start_time, end_time, change_number):
    ''' Function to close the change task by taking a change number 
        as an input which also automatically close the change request '''
    
    # Set your variables in .env file 
    snow_username = os.getenv('SN_USER')
    snow_password = os.getenv('SN_PASS')
    slack_token = os.getenv('SLACK_TOKEN')
    snow_inst = os.getenv('SNOW_INST')
    
    # Define your slack channel name 
    slack_channel = 'webhooktesting'
    
    #Initialize the status code for the snow change 
    response_code = 0 
    
    try:
        headers = {
                "Accept":"application/json",
                "Content-Type":"application/json"
                }
        
        # To get the details of change request using change number in JSON format
        url = f'https://{snow_inst}/api/now/table/change_request?sysparm_query=number={change_number}&displayvalue=true'
        
        # HTTP GET Method to retrieve the change request details 
        response = requests.get(url, auth=(snow_username, snow_password), headers=headers)
        
        # deserialized the response into Python dictionary 
        response_py = response.json()
        #print(response_py)
        
        # Parsing the change creater and change request sys_id
        change_req_user = response_py['result'][0]['sys_created_by']
        change_desc = response_py['result'][0]['short_description']
        change_req_sys_id = response_py['result'][0]['sys_id']
        
        # To get the details of change task via change request sys_id in XML format
        url = f'https://{snow_inst}/api/now/table/change_task?sysparm_query=change_request={change_req_sys_id}&displayvalue=true'
        
        # HTTP GET Method to retrieve the change task details 
        response = requests.get(url, auth=(snow_username, snow_password), headers=headers)
        response_py = response.json()
        
        # Parsing the change task sys_id
        change_task_sys_id_impl = response_py['result'][0]['sys_id']
        change_task_sys_id_post = response_py['result'][1]['sys_id']
        #print(change_task_sys_id_impl)
        #print(change_task_sys_id_post)
        
        # update the implementation change task via PUT HTTP method 
        url = f'https://{snow_inst}/api/now/table/change_task/{change_task_sys_id_impl}'
        
        data_json = f'''{{
                "change_task_type":"Review",
                "close_code":"successful",
                "close_notes":"completed successfully.",
                "state":"3"
                }}'''
        
        response = requests.put(url, auth=(snow_username, snow_password), headers=headers, data=data_json)
        
        # save the response status code in a variable 
        #response_code = response.status_code
        
        # deserialized the response into Python dictionary 
        #response_py = response.json()
        
        # serialize the response back to json and display in pretty format  
        #response_json = json.dumps(response_py, indent=2)
        #print(response_json)
        
        if response.status_code != 200: 
            print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.content)
            exit(1)
            
        if response.status_code == 200:
            # update the post implementation change task via PUT HTTP method after the above task closure 
            url = f'https://{snow_inst}/api/now/table/change_task/{change_task_sys_id_post}'
            response = requests.put(url, auth=(snow_username, snow_password), headers=headers, data=data_json)
            
            if response.status_code != 200: 
                print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.content)
                exit(1)
            
            if response.status_code == 200:
                # update the change request via PUT HTTP method after the above tasks are closed 
                url = f'https://{snow_inst}/api/now/table/change_request/{change_req_sys_id}'
                
                data_json = f'''{{
                                "work_start":"{start_time}",
                                "work_end":"{end_time}",
                                "close_code":"successful",
                                "close_notes":"completed successfully.",
                                "state":"3"
                                }}'''
                
                response = requests.put(url, auth=(snow_username, snow_password), headers=headers, data=data_json)
                response_code = response.status_code
                
                if response_code != 200: 
                    print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.content)
                    exit(1)
                if response_code == 200:
                    client = WebClient(token=slack_token)
                    client.chat_postMessage(channel=slack_channel, 
                                    text=f'{change_number}: {change_desc }, has been closed successfully.')
        else:
            pass
        
        return response_code
        
    except Exception as e:
        print(Fore.RED + "~" * 10 + str(e) + "~" * 10 + Style.RESET_ALL)

if __name__ == '__main__':

    # start time of the change
    start_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Define change number as variable string or take a user input
    change_number = 'CHG0030011'
    #change_number = (input('please enter the change number: ')).strip()

    # end time of the change
    end_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # change_close(username, password, start_time, end_time, change_number)
    change_close(start_time, end_time, change_number)