import os
import requests
from transformers import AutoTokenizer
import string

import csv

data = []
with open('data.csv', 'r') as csvfile: 
    reader = csv.reader(csvfile, skipinitialspace=True)
    data.append(tuple(next(reader)))
    for date, shift, pat, day, staff, wait in reader:
        data.append((date, shift, int(pat), int(day), int(staff), int(wait)))       

url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"

body = {
	"project_id": "7266e034-8bcc-40a5-a222-440243471013",
	"model_id": "ibm/granite-3-3-8b-instruct",
	"frequency_penalty": 0,
	"max_tokens": 4000,
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
          "text": """
					please analyze trends in the data to predict the amount of er patients coming in each day each shift then please predict how much staff should be called in each shift to keep wait times close to ideal for the next one month after the end of the dataset in this format [Date Shift Predicted_Patients Day Suggested_Staff Predicted_Wait]
            		it is important to follow this mapping: monday = 0, tuesday = 1, wednesday = 2, thursday = 3, friday = 4, saturday = 5, sunday = 6
                    ideal wait time - 30min
					maximum avalible staff - 40
					minimize the amount of staff on board while also trying to keep to the average wait time or lower

                    Date refers to the date 
                    shift refers to if the working shift is AM or PM
                    pat refers to number of patients coming in during that shift
                    day refers to the day of the week witeen as a number: monday(0) tuesday(1) wednesday(2) thursday(3) friday(4) saturday(5) sunday(6)
                    staff refers to the amount of staff working that shift
                    wait refers to the average wait time in minutes
                    
                    only predict for the next month '2025-04-01' to '2025-04-30' 
                    '2025-04-01' starts on a tuesday = 1 so day would = 1
                    do not provide an explanation
                    only output the results table and nothing else: [[Date Shift Predicted_Patients Day Suggested_Staff Predicted_Wait]]
                    day should be outputed as a number: monday = 0, tuesday = 1, wednesday = 2, thursday = 3, friday = 4, saturday = 5, sunday = 6
                    do not put a new line between entries
                    example output: [["2025-04-01", "AM", 25, 1, 7, 23], ["2025-04-01", "PM", 25, 1, 7, 23],]
                    
                    [DATA]""" + str(data)
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

print(data["choices"][0]["message"]["content"])
