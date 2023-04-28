import win32com.client as win32
import os
import datetime
import json
from dotenv import load_dotenv


load_dotenv()

os.chdir(os.environ.get("MAIN_DIR"))

dagen = datetime.date.today()
veckonummer = dagen.isocalendar()[1]

veckodagar = {
    0:"måndag",
    1:"tisdag",
    2:"onsdag",
    3:"torsdag",
    4:"fredag",
    5:"lördag",
    6:"söndag"
}

with open(os.path.join("Data", "Cafe117", f"Vecka {veckonummer}", f"meny_vecka_{veckonummer}.json"), "r", encoding="utf-8") as fp:
    veckans_meny = json.load(fp)

dagens_meny = veckans_meny["veckodagar"][veckodagar[datetime.datetime.weekday(dagen)]].values()
dagens_meny_string = ""
for alternativ in dagens_meny:
    dagens_meny_string += "&emsp;* " + alternativ + "<br>"

if dagen.weekday() == 0:
    intressanta_dagen = dagen - datetime.timedelta(days=3)  # Om måndag, ta fredag
else:
    intressanta_dagen = dagen - datetime.timedelta(days=1)  # Annars, ta gårdagen




outlook = win32.Dispatch("outlook.application")

mail = outlook.CreateItem(0)
mail.Subject = "Morgonhälsning " + dagen.strftime("%Y-%m-%d")

with open("maillista.txt", "r", encoding="utf-8") as f:
    personer = [line.strip("\n") for line in f.readlines()]


mail_list_string = ""
for idx, pers in enumerate(personer):
    mail_list_string += f"; {pers}" if idx != 0 else f"{pers}"

mail.To = mail_list_string


img_path = os.path.join(os.getcwd(), "Data", "Kontorsaktivitet", "kontorsaktivitet_"+intressanta_dagen.strftime('%Y-%m-%d')+".png")
img_path2 = os.path.join(os.getcwd(), "Data", "SMHI", "SMHI_dagsprognos_"+dagen.strftime('%Y-%m-%d')+".png")

# Kontorsaktivitet
attachment1 = mail.Attachments.Add(img_path)
attachment1.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "MyId1")

# SMHI
attachment2 = mail.Attachments.Add(img_path2)
attachment2.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "MyId2")

igar_eller_fredag_text = "igår" if dagen.weekday() != 0 else "i fredags"



mail.HTMLBody = f"""
<HTML><BODY>
<span style="color:red;background:black;font-size:large">OBS</span> - <em>Detta är ett mail som blivit skickat automatiskt.</em><br><br>

Godmorgon denna vackra {veckodagar[datetime.datetime.weekday(dagen)]}!<br><br>

Såhär såg det ut på kontoret <span style="color: green">{igar_eller_fredag_text}</span>:<br><br>

<img src="cid:MyId1" width=450 height=400><br><br>

Detta är <span style="color: green">väderprognosen</span> för idag:<br><br>
<img src="cid:MyId2" width=450 height=35><br><br>

Här är <span style="color: green">dagens meny</span> hos Café 117:<br>
{dagens_meny_string}<br>


(*) Den genomsnittliga kontorstiden bygger på totalt antal minuter på kontoret dividerat med maxbeläggning, 
dvs. arean under kurvan. Den är inte ekvivalent med faktisk arbetad tid per anställd.
Sensorn startar om på noll vid 00:00 och är inte 100% exakt, vilket kan ge upphov till negativt antal personer.
<br><br>

Mvh,<br>
Oscar
</BODY></HTML>
"""

mail.Send()
