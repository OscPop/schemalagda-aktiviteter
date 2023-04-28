from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from PIL import Image
import os
import pandas as pd
import requests
import datetime
from dotenv import load_dotenv


load_dotenv()

date = datetime.date.today().strftime("%Y-%m-%d")

os.chdir(os.environ.get("MAIN_DIR"))

URL = r"https://www.smhi.se/vader/prognoser/ortsprognoser/q/Stockholm/2673730"

driver = webdriver.Edge()
driver.maximize_window()
driver.get(URL)
time.sleep(3)

element = driver.find_element(By.CLASS_NAME, "tLGiB")

# Testa att klicka ner pop-up om den finns (hårdkodad och kanske crashar)
try:
    driver.find_element(By.XPATH, "/html/body/div[5]/div[2]/div[1]").click()
except Exception as e:
    pass
driver.save_screenshot("SMHI_screenshot.png")

location = element.location
size = element.size

x = location["x"]+198
y = location["y"]+152*2
w = size["width"]*1.5
h = size["height"]*1.45
width = x + w
height = y + h

im = Image.open("SMHI_screenshot.png")
im = im.crop((int(x), int(y), int(width), int(height)))
im.save(os.path.join("Data", "SMHI", f"SMHI_dagsprognos_{date}.png"))
os.remove(f"SMHI_screenshot.png")

content = driver.page_source.encode("utf-8").strip()
driver.close()