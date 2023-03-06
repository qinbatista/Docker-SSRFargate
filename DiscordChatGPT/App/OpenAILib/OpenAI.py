from dotenv import load_dotenv
import os
import requests
import json
load_dotenv()
url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer "+os.getenv("CHATGPT_API_KEY")
}


def chatgpt_response(prompt):
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }
    response_dict = requests.post(url, headers=headers, data=json.dumps(data)).json().get('choices')
    if response_dict and len(response_dict) > 0:
        return response_dict[0]['message']['content']
