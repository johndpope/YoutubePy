import pickle
import os, time, datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import constants

def get_time():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

def save_cookie(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)
    print(get_time(), f'cookie saved at {path}')

def load_cookie(driver, path):
    with open(path, 'rb') as cookies_file:
        cookies = pickle.load(cookies_file)
        for cookie in cookies:
            driver.add_cookie(cookie)

driver = webdriver.Chrome(constants.CHROME_DRIVER_PATH)

goog_url = "https://accounts.google.com/signin/v2/identifier"
driver.get(goog_url)

goog_email_element = driver.find_element_by_id("identifierId")
goog_email_element.send_keys(constants.GOOG_ID)
goog_email_element.send_keys(Keys.ENTER)
time.sleep(2)

goog_pass_element = driver.find_element_by_xpath("//*[@id='password']/div[1]/div/div[1]/input")
goog_pass_element.send_keys(constants.GOOG_PASS)
goog_pass_element.send_keys(Keys.ENTER)
save_cookie(driver, '/tmp/YCTW_google_cookie')
time.sleep(2)

driver.quit()
