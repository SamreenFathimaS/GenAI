import pyautogui
import time

# Wait 5 seconds to let you get ready
time.sleep(5)

# 1️⃣ Open Windows Start
pyautogui.press('win')
time.sleep(1)

# 2️⃣ Type your browser name (example: chrome)
pyautogui.write('chrome', interval=0.1)
time.sleep(1)

# 3️⃣ Press Enter to open browser
pyautogui.press('enter')

# Wait for browser to open
time.sleep(5)

# 4️⃣ Click address bar (update x,y for your screen)
pyautogui.click(x=400, y=50)
time.sleep(1)

# 5️⃣ Type Gmail URL
pyautogui.write('https://mail.google.com/', interval=0.05)
pyautogui.press('enter')

# Wait for Gmail to load fully
time.sleep(10)

# 6️⃣ Click Compose button (update x,y!)
pyautogui.click(x=100, y=200)
time.sleep(3)

# 7️⃣ Type recipient email
pyautogui.write('socialeagle.ai@gmail.com', interval=0.05)
pyautogui.press('tab')  # move to Subject field
time.sleep(1)

# 8️⃣ Type Subject
pyautogui.write('Test Mail From Samreen Fathima', interval=0.05)
pyautogui.press('tab')  # move to Body field
time.sleep(1)

# 9️⃣ Type Body
pyautogui.write('Hello, this is a test email sent using pyautogui automation.', interval=0.05)

# 1️⃣0️⃣ Send the mail with Ctrl+Enter
pyautogui.hotkey('ctrl', 'enter')
