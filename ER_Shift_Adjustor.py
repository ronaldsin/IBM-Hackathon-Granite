import csv
import requests
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document




class ERShiftDocument:
    def __init__(self, id, text):
        self.page_content = text
        self.metadata = {"id": id}
    
    @property
    def id(self):
        return self.metadata["id"]



def load_er_data(filename='data.csv'):
    docs = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            text = (
                f"{row['date']} {row['shift']} shift | "
                f"Patients: {row['patients']}, Staff: {row['staff']}, "
                f"Wait: {row['waittime']} min, Day: {row['dayofweek']}"
            )
            metadata = {"id": f"{row['date']}_{row['shift']}"}
            docs.append(Document(page_content=text, metadata=metadata))
    return docs


documents = load_er_data('data.csv')



embeddings_model_path = "ibm-granite/granite-embedding-30m-english"
embeddings_model = HuggingFaceEmbeddings(model_name=embeddings_model_path)



query = "Saturday ER PM shift with 38 patients, 9 staff, and 44 minute wait"



retrieved_docs = vector_db.similarity_search(query, k=3)
retrieved_texts = [doc.page_content for doc in retrieved_docs]


rag_prompt = f"""
Current Situation:
{query}

Similar Historical Shifts:
{chr(10).join(retrieved_texts)}

Recommendation:
Based on these similar cases, suggest an action plan for the current shift.
Respond only with the recommended actions (e.g., "Add 2 more staff", "Move ICU nurse to ER", etc.)
"""

print("Prompt sent to Granite API:")
print(rag_prompt)



url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + os.getenv('BEARER_TOKEN')
}

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
            "content": rag_prompt
        }
    ]
}

response = requests.post(url, headers=headers, json=body)
if response.status_code != 200:
    raise Exception(f"API returned status {response.status_code}: {response.text}")

result = response.json()

print("\nGranite LLM response:")
print(result["choices"][0]["message"]["content"])
