import os
import requests
from bs4 import BeautifulSoup as BS
import pandas as pd
import json
import datetime
from dotenv import load_dotenv


load_dotenv()

os.chdir(os.environ.get("MAIN_DIR"))

URL = "https://cafe117.se/"

resp = requests.get(URL)
soup = BS(resp.content, "html.parser")

meny_dict = {}
lines = []
vecka = datetime.date.today().isocalendar()[1]
meny_dict["veckonummer"] = vecka
meny_dict["veckodagar"] = {}

veckans = soup.find("ul", {"id":"Veckanslunch"})
veckans = veckans.find_all("li")[:-1]
for dag in veckans:
    divs = dag.find_all("div")
    lines.append(divs[0].text)
    #print(divs[0].text)
    meny_dict["veckodagar"][divs[0].text.lower()] = {}
    alternativ = divs[1].find_all("p")
    for idx, alt in enumerate(alternativ):
        lines.append(f"* {alt.text}")
        #print("*", rätt.text)
        meny_dict["veckodagar"][divs[0].text.lower()][f"alt_{idx+1}"] = alt.text
        


# Spara data både som textfil, men också som json
folder_path = os.path.join("Data", "Cafe117", f"Vecka {vecka}")
if not os.path.isdir(folder_path):
    os.makedirs(folder_path)

file_name = f"meny_vecka_{vecka}"

# Textfil
with open(os.path.join(folder_path, f"{file_name}.txt"), "w", encoding="utf-8") as f:
    for line in lines:
        f.write(line+"\n")

# Json
with open(os.path.join(folder_path, f"{file_name}.json"), "w", encoding="utf-8") as f:
    json.dump(meny_dict, f, ensure_ascii=False, indent=4)