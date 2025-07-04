import pyautogui
import time

# Wait a few seconds so you have time to prepare
time.sleep(3)

# 1️⃣ Press Windows key to open start menu (on Windows)
pyautogui.press('win')
time.sleep(1)

# 2️⃣ Type your browser name, e.g., 'chrome'
pyautogui.write('chrome', interval=0.1)
time.sleep(1)

# 3️⃣ Press Enter to open the browser
pyautogui.press('enter')

# Wait for browser to open
time.sleep(3)

# 4️⃣ Click the address bar (approx position — adjust as needed!)
pyautogui.click(x=400, y=50)
time.sleep(0.5)

# 5️⃣ Type the search query
pyautogui.write('south africa vs australia score', interval=0.05)
pyautogui.press('enter')

# Wait for results to load
time.sleep(5)

# 6️⃣ Click the first link (approx position — adjust!)
pyautogui.click(x=400, y=300)
