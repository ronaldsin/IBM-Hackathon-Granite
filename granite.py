import os
import requests


url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"

body = {
	"project_id": "7266e034-8bcc-40a5-a222-440243471013",
	"model_id": "ibm/granite-3-3-8b-instruct",
	"frequency_penalty": 0,
	"max_tokens": 2000,
	"presence_penalty": 0,
	"temperature": 0,
	"top_p": 1,
	"messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Who won league of legends worlds championship 2013?"
        }
      ]
    },
  	],

}

headers = {
	"Accept": "application/json",
	"Content-Type": "application/json",
	"Authorization": "Bearer " + os.getenv('BEARER_TOKEN')
	
}

response = requests.post(
	url,
	headers=headers,
	json=body
)

if response.status_code != 200:
	raise Exception("Non-200 response: " + str(response.text))

data = response.json()