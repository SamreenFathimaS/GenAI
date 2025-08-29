def add(a, b):
    return a + b

def add_average(a, b):
    return (a + b) / 2

a, b = 5, 3
print("Sum:", add(a, b))
print("Average:", add_average(a, b))





import pyautogui

pyautogui.moveTo(100, 200)   # Move mouse
pyautogui.click()
pyautogui.typewrite("Hello RPA with Python!", interval=0.1)
