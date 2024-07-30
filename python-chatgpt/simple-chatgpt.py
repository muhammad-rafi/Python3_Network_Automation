import os
import openai

# source .envrc 
# Run the above command if you are using '.envrc' file and not using 'direnv'
# https://shivamarora.medium.com/a-guide-to-manage-your-environment-variables-in-a-better-way-using-direnv-2c1cd475c8e
# https://www.youtube.com/watch?v=Vurdg6yrPL8

openai.api_key = os.environ["OPENAI_API_KEY"]
print(openai.api_key)

query = input('What is your question: ')
messages = [
            {"role": "system", "content": "You are a chatbot"},
            {"role": "user", "content": f"{query}"},
        ]

response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages
                        )

result = ''
for choice in response.choices:
    result += choice.message.content

print(f"We asked chatGPT { question } - Here Is there Answer:")
print("-----------------------------------------------------------------")
print(result)