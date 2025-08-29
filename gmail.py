import pyautogui
import webbrowser
import time

# 1. Open Gmail in browser
webbrowser.open("https://mail.google.com/")
time.sleep(8)  # wait for Gmail to load fully (increase if slow internet)

# 2. Click "Compose" button
# 👇 Replace with your own coordinates using pyautogui.position()
pyautogui.moveTo(102, 342, duration=1)  # Example coords for Compose
pyautogui.click()
time.sleep(3)

# 3. Type recipient email
pyautogui.typewrite("visit.munavar@gmail.com", interval=0.1)
time.sleep(1)
pyautogui.press("tab")  # move to subject field
time.sleep(3)

# 4. Type subject
pyautogui.typewrite("Hello from Samreen! Don't use mobile phone much time it will affect you lot", interval=0.1)
pyautogui.press("tab")  # move to body field
time.sleep(1)

# 5. Type message
pyautogui.typewrite("Hi Munavar,\n\nThis is Samreen Just care me give me some time.\n\nRegards,\nPython Bot", interval=0.05)
time.sleep(1)

# 6. Send email (Ctrl + Enter shortcut)
pyautogui.hotkey("ctrl", "enter")

print("✅ Email sent successfully!")
