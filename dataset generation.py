import pandas as pd
import numpy as np
from datetime import datetime, timedelta

startdate = "2025-01-01"
days = 90
shifts = ["AM", "PM"]
crisisstart = "2025-02-15"
crisisend = "2025-02-28"

datelist = []
for day in range(days):
    currentdate = (datetime.strptime(startdate, "%Y-%m-%d") + timedelta(days=day))
    for shift in shifts:
        datelist.append((currentdate, shift))
df = pd.DataFrame(datelist, columns=["date", "shift"])

df["date"] = pd.to_datetime(df["date"])

def generatepatients(mean, size):
    base = np.random.poisson(mean, size)
    modifier = np.where(
        np.random.random(size) < 0.2,
        np.random.choice([1.25, 0.75], size),
        1.0
    )
    return np.clip((base * modifier).astype(int), 1, None)

df["patients"] = np.where(
    df["shift"] == "AM",
    generatepatients(32, len(df)),
    generatepatients(42, len(df))
)

def apply_busy_patterns(df):
    df["dayofweek"] = df["date"].dt.dayofweek
    df.loc[df["dayofweek"] == 0, "patients"] = (df.loc[df["dayofweek"] == 0, "patients"] * 1.25).astype(int)
    df.loc[(df["dayofweek"] == 4) & (df["shift"] == "PM"), "patients"] = (df.loc[(df["dayofweek"] == 4) & (df["shift"] == "PM"), "patients"] * 1.3).astype(int)
    df.loc[(df["dayofweek"] == 5) & (df["shift"] == "AM"), "patients"] = (df.loc[(df["dayofweek"] == 5) & (df["shift"] == "AM"), "patients"] * 1.4).astype(int)
    return df

df = apply_busy_patterns(df)

df["staff"] = np.where(
    df["shift"] == "AM",
    generatepatients(11, len(df)),
    generatepatients(13, len(df))
)

crisis = (df["date"] >= pd.to_datetime(crisisstart)) & \
         (df["date"] <= pd.to_datetime(crisisend))
df.loc[crisis, "patients"] = (df.loc[crisis, "patients"] * 2.0).astype(int)
df.loc[crisis, "patients"] += np.random.randint(3, 12, sum(crisis))

def calculatewaittime(patients, staff, iscrisis):
    ratio = patients / max(1, staff)
    waittime = 20 + (ratio ** 1.1) * 3
    if iscrisis:
        waittime *= 1.5
    waittime *= np.random.uniform(0.95, 1.05)
    return int(round(waittime))

df["waittime"] = df.apply(
    lambda row: calculatewaittime(
        row["patients"],
        row["staff"],
        crisis[row.name]
    ),
    axis=1
)

df.to_csv("data.csv", index=False)