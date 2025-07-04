import pyautogui
import time

#mouse opertaion

pyautogui.click(99,234)
time.sleep(2)
pyautogui.rightClick(100, 100)

time.sleep(4)
pyautogui.click(624, 77)
pyautogui.doubleClick(100, 100)
pyautogui.drag(100,100)
pyautogui.scroll(500)


#keyboard operations

time.sleep(2)
pyautogui.click(911, 180)
pyautogui.typewrite("Socialeagle.ai")
time.sleep(3)
pyautogui.hotkey('ctrl','a')

#image

location = pyautogui.locateOnScreen('copilot.png', confidence=0.8)
print(location)
time.sleep(2)
pyautogui.click(pyautogui.center(location))

pyautogui.size()
SS = pyautogui.screenshot()
SS.save("demo.png")