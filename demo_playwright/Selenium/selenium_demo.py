from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
driver.get("https://the-internet.herokuapp.com/login")

driver.back()
driver.forward()
driver.refresh()

# Locate username input
wait = WebDriverWait(driver, 10)
username_input = wait.until(EC.presence_of_element_located((By.ID, 'username')))

# Type username
username_input.send_keys("tomsmith")

#Press Enter on password field
password_input = driver.find_element(By.ID, 'password')
password_input.send_keys("SuperSecretPassword!")
password_input.send_keys(Keys.ENTER)

# Take screenshot
driver.save_screenshot("demo1.png")

driver.quit()

