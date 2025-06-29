import os
import requests
import csv
import random
from datetime import datetime, timedelta

alldata = []
with open('data.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        alldata.append({
            "date": datetime.strptime(row['date'], "%Y-%m-%d"),
            "shift": row['shift'],
            "patients": int(row['patients']),
            "day": int(row['dayofweek']),
            "staff": int(row['staff']),
            "wait": int(row['waittime'])
        })

validstartdates = [row["date"] for row in alldata[:-6]]
startdate = random.choice(validstartdates)
enddate = startdate + timedelta(days=6)

weekdata = [row for row in alldata if startdate <= row["date"] <= enddate]

formatteddata = [[
    row["date"].strftime("%Y-%m-%d"),
    row["shift"],
    row["patients"],
    row["day"],
    row["staff"],
    row["wait"]
] for row in weekdata]

prompttext = f"""
Summarize this 7-day ER shift performance. For each shift, include:
- Whether the ER was under, at, or over capacity
- Staff-to-patient ratio
- Any risk indicators (e.g., high wait time, low staffing)

Format: [Date, Shift, Summary]

[DATA]{formatteddata}
"""

url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + os.getenv('BEARER_TOKEN')
}

body = {
    "projectid": "7266e034-8bcc-40a5-a222-440243471013",
    "modelid": "ibm/granite-3-3-8b-instruct",
    "frequencypenalty": 0,
    "maxtokens": 4000,
    "presencepenalty": 0,
    "temperature": 0,
    "topp": 1,
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
                    "text": prompttext
                }
            ]
        }
    ]
}

response = requests.post(url, headers=headers, json=body)

if response.status_code != 200:
    raise Exception("Non-200 response: " + str(response.text))

result = response.json()
print(result["choices"][0]["message"]["content"])
