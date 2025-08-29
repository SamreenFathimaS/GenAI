import pyautogui

#pyautogui.moveTo(100, 200)   # Move mouse
#pyautogui.click()
#pyautogui.typewrite("Hello RPA with Python!", interval=0.1)


import pyautogui
import time
import webbrowser

# 1. Open browser
webbrowser.open("https://www.google.com")
time.sleep(3)  # wait for browser to open

# 2. Type search query
pyautogui.moveTo(1202, 572, duration=1)
pyautogui.typewrite("What was the score between South Africa and Australia?", interval=0.1)
pyautogui.press("enter")
time.sleep(3)  # wait for results to load

# 3. Move mouse & click first link
# ⚠️ Coordinates depend on your screen resolution & browser layout
# To find coordinates: run pyautogui.position() while hovering mouse
pyautogui.moveTo(575, 946, duration=1)  # example position for first link
pyautogui.click()

print("Task Completed ✅")
