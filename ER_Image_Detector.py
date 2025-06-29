import os
import csv
import base64
import io
from PIL import Image, ImageOps
from langchain_community.llms import Replicate
from transformers import AutoTokenizer, AutoProcessor

replicateapikey = "REPLICATEAPITOKENHERE"
visionmodelpath = "ibm-granite/granite-vision-3.2-2b"
visionmodel = Replicate(
    model=visionmodelpath,
    replicate_api_token=replicateapikey,
    model_kwargs={"max_tokens": 800, "min_tokens": 100},
)

visionprocessor = AutoProcessor.from_pretrained(visionmodelpath)

modelpath = "ibm-granite/granite-3.3-8b-instruct"
model = Replicate(
    model=modelpath,
    replicate_api_token=replicateapikey,
    model_kwargs={"max_tokens": 1500, "min_tokens": 200},
)

tokenizer = AutoTokenizer.from_pretrained(modelpath)

def encodeimage(imagepath):
    image = Image.open(imagepath)
    image = ImageOps.exif_transpose(image).convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def loaddata(filepath):
    data = []
    with open(filepath, "r") as csvfile:
        reader = csv.reader(csvfile, skipinitialspace=True)
        headers = next(reader)
        data.append(tuple(headers))
        for row in reader:
            date, shift, pat, day, staff, wait = row
            data.append((date, shift, int(pat), int(day), int(staff), int(wait)))
    return data

def parse_constraints(imagedescription):
    constraints = {
        "max_staff": 40,
        "blackout_dates": [],
        "extra_staff": 0
    }
    
    if "MAX" in imagedescription and "STAFF" in imagedescription:
        parts = imagedescription.split()
        try:
            constraints["max_staff"] = int(parts[parts.index("MAX") + 1])
        except (ValueError, IndexError):
            pass
    
    if "NO OT" in imagedescription:
        parts = imagedescription.split()
        try:
            date_index = parts.index("NO") + 2
            while date_index < len(parts):
                date_str = parts[date_index].strip()
                if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
                    constraints["blackout_dates"].append(date_str)
                date_index += 1
        except (ValueError, IndexError):
            pass
    
    if "EXTRA" in imagedescription:
        parts = imagedescription.split()
        try:
            constraints["extra_staff"] = int(parts[parts.index("EXTRA") + 1])
        except (ValueError, IndexError):
            pass
    
    return constraints

def runforecast(data, imagedescription):
    constraints = parse_constraints(imagedescription)
    max_staff = constraints["max_staff"]
    blackout_dates = constraints["blackout_dates"]
    
    userprompt = f"""
STRICTLY follow these rules to adjust the ER schedule based on the whiteboard constraints:

**Constraints from Whiteboard**:
{imagedescription}

**Adjustment Rules**:
1. BLACKOUT DATES ({blackout_dates}): Reduce staff by 30-50% (prioritize PM shifts)
2. NO OT DATES: Cap shifts at 8 hours (reduce staff by ~33% if original shift was 12h)
3. MAX STAFF: Never exceed {max_staff} (from whiteboard)
4. PROCEDURE CANCELLATIONS: Subtract 5-7 support staff if elective procedures paused

**Output Format**:
- ONLY show rows where staff numbers CHANGE
- Format as markdown table with: Date | Shift | Original Staff | Adjusted Staff | Reason
- If no changes needed, say: "No adjustments required for the specified constraints."

**Current Schedule**:
{data}

**Critical Instructions**:
- ONLY modify dates matching the EXACT blackout/OT dates from the whiteboard
- For blackouts: Reduce PM shifts by 50%, AM shifts by 30%
- Round staff numbers DOWN (e.g., 17 → 8 for 50% reduction)
- NEVER show unchanged rows
"""
    prompt = tokenizer.apply_chat_template(
        conversation=[{"role": "user", "content": userprompt}],
        add_generation_prompt=True,
        tokenize=False,
    )
    return model.invoke(prompt)

if __name__ == "__main__":
    datapath = "data.csv"
    imagepath = "hackathonima.png"

    hospitaldata = loaddata(datapath)
    imageuri = encodeimage(imagepath)

    visionprompt = visionprocessor.apply_chat_template(
        conversation=[{
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": "Extract all scheduling constraints from this whiteboard, including MAX STAFF numbers, BLACKOUT DATES (NO OT), and EXTRA STAFF notations. Return the exact text."}
            ]
        }],
        add_generation_prompt=True,
    )

    imagedescription = visionmodel.invoke(visionprompt, image=imageuri)
    print(f"Raw image description: {imagedescription}")  

    forecast = runforecast(hospitaldata, imagedescription)
    print(forecast)
