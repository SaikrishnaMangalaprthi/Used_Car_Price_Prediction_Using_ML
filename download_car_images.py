from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import requests
import os
import time
print("SCRIPT STARTED")
car_name = "Audi A4"

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)

driver.get(
    f"https://www.google.com/search?tbm=isch&q={car_name}+car"
)

time.sleep(3)

images = driver.find_elements(By.TAG_NAME, "img")

for img in images:
    src = img.get_attribute("src")

    if src and src.startswith("http"):
        try:
            response = requests.get(src, timeout=10)

            with open("audi_a4.jpg", "wb") as f:
                f.write(response.content)

            print("Downloaded!")
            break

        except:
            pass

driver.quit()