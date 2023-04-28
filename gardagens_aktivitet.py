import pandas as pd
import requests
import json
import datetime
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv


load_dotenv()

os.chdir(os.environ.get("MAIN_DIR"))

# API setup och hämta authentication token
url1 = r"https://api.imas.net/account/login"
myobj = {
  "userName": os.environ.get("IMAS_API_USERNAME"),
  "password": os.environ.get("IMAS_API_PASSWORD"),
  "resource": "sw"
}
headers1 = {"Content-Type": "application/json"}
response1 = requests.post(url1, json=myobj, headers=headers1)
auth_token = response1.text


# Hämta data från dag 'date' med upplösningen "interval"
today = datetime.date.today()
if today.weekday() == 0:                                # Om måndag
  date = today - datetime.timedelta(days=3)   # Fredagens data
else:       
  date = today - datetime.timedelta(days=1)   # Gårdagens data

date_str = date.strftime("%Y-%m-%dT00")    # Formattera om som string

interval = 1    # Upplösning i minuter 

# Nytt API-anrop för att få ut info om gårdagen
url2 = f"https://api.imas.net/export/exportintervalvisits?id=stockholm&from={date_str}%3A00%3A00&until={date_str}%3A00%3A00&groupInterval={interval}&onlyOpenedHours=false"
headers2 = {
"Accept":"application/json",
"X-Auth-Token":auth_token[1:-1]}
response2 = requests.get(url2, headers=headers2)
parsed = json.loads(response2.content)


# Gör en pandas dataframe av json-filen
df = pd.DataFrame(parsed)

df["date"] = df.dateTime.str[0:10]
df["time"] = df.dateTime.str[11:]
df = df[["dateTime",  "date", "time", "incoming", "outgoing"]]
df.sort_values(by="dateTime", inplace=True, ignore_index=True)
df["change"] = df.incoming - df.outgoing
df["current"] = pd.Series(np.zeros(df.shape[0]))


# Lägg till data i 'current'-kolumnen
# Antar att det är 0 i början (i detta fall 00:00) och sätter negativa värden till 0
df.current = df.change.cumsum()


range_stop = int(df.time.to_numpy()[-1][0:2]) + 1

#dagens_datum = (datetime.date.today()-datetime.timedelta(days=1)).strftime("%Y-%m-%d")

date = date.strftime("%Y-%m-%d")

sns.set_style("darkgrid")

fig, ax = plt.subplots(figsize=(8,6))

ax.set_xticks(range(0,range_stop*60,60),  range(0,range_stop))
ax.set_ylabel("Antal", fontsize=15)
ax.set_xlabel("Tid", fontsize=15)
ax.set_title("Kontorsaktivitet " + date, fontsize=20)

max_pers = df.current.max()

if max_pers >= 1:
    sns.lineplot(data=df, x="time", y="current", ax=ax)
    tidigast = df.query("change != 0").iloc[0].time[:-3]
    senast = df.query("change != 0").iloc[-1].time[:-3]  # ändra denna så att den går på ändirng i folk?

    max_pers_tid = df.loc[df.current == max_pers].iloc[0].time[:-3]
    avg_minutes_person = df.query("current > 0").current.sum() / max_pers
    avg_hours, avg_minutes = avg_minutes_person //60, (avg_minutes_person-60 * (avg_minutes_person // 60))

    textstr = f"""Genomsnittlig kontorstid*:\n{int(avg_hours)} h {int(avg_minutes)} min
Maxbeläggning:\n{max_pers} personer (kl. {max_pers_tid})
Tidigaste aktivitet: {tidigast}
Senaste aktivitet:   {senast}"""

else:
   textstr = f"""Ingen aktivitet på 
kontoret denna dag ... """

props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
font = {"family":"monospace",
        "color":"black",
        "size":8}
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, verticalalignment="top", bbox=props, fontdict=font)

fig.savefig(os.path.join("Data", "Kontorsaktivitet", r"kontorsaktivitet_"+date+".png"))
#fig.savefig("test.png")
df.to_csv(os.path.join("Data", "Kontorsaktivitet", r"kontorsaktivitet_"+date+".csv"), sep=",", index=False)