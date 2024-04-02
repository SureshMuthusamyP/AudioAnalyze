import requests
from dotenv import load_dotenv
import os
load_dotenv()



API_KEY = os.getenv("Chat_api")
API_ENDPOINT = 'https://api.openai.com/v1/chat/completions'


class process():
    def send_message(self,message):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(API_KEY)
        }
        data = {
            'model': 'gpt-3.5-turbo', 
            'messages': [{'role': 'user', 'content': message}],
        }
        response = requests.post(API_ENDPOINT, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return 'Error: {}'.format(response.text)
