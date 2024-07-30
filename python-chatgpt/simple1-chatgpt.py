import requests
import openai
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

URL = "https://api.openai.com/v1/chat/completions"

payload = {
    # "model": "gpt-3.5-turbo",
    "model": "text-davinci-003",
    "messages": [{"role": "user", 
                  "content": f"What is the first computer in the world?"}],
    "temperature" : 1.0,
    "top_p":1.0,
    "n" : 1,
    "stream": False,
    "presence_penalty":0,
    "frequency_penalty":0,
}

headers = {
"Content-Type": "application/json",
"Authorization": f"Bearer {openai.api_key}"
}

response = requests.post(URL, headers=headers, json=payload, stream=False)

# print(dir(response))

# print(response.content)
# print(response.content.decode().strip())
print(response.json())
# print(response.raw)
# print(response.status_code)
# print(response.text)
# print(response.reason)
# print(response.raise_for_status)
# print(response.url)
# print(response.request)
