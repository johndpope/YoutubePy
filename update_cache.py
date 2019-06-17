import os, datetime, time, sys, pickle
from random import randint
import re
import requests
import random
import constants

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, \
    UnexpectedAlertPresentException, WebDriverException

from bs4 import BeautifulSoup
from pip._vendor.distlib.util import proceed

from urllib.request import Request, urlopen

def get_time():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

def load_cookie(driver, path):
    with open(path, 'rb') as cookies_file:
        cookies = pickle.load(cookies_file)
        for cookie in cookies:
            driver.add_cookie(cookie)

def login(driver):
    driver.get('https://accounts.google.com/ServiceLogin?continue=https%3A%2F%2Fwww.youtube.com%2Ffeed%2Fhistory%2Fcomment_history')
    goog_email_element = driver.find_element_by_id("identifierId")
    goog_email_element.send_keys(constants.GOOG_ID)
    goog_email_element.send_keys(Keys.ENTER)
    time.sleep(2)

    goog_pass_element = driver.find_element_by_xpath("//*[@id='password']/div[1]/div/div[1]/input")
    goog_pass_element.send_keys(constants.GOOG_PASS)
    goog_pass_element.send_keys(Keys.ENTER)
    return driver

if __name__ == "__main__":
    argv = sys.argv[1:]
    d = {}
    for i in range(0, len(argv), 2):
        d[argv[i].replace('-', '')] = argv[i + 1]
    print(get_time(), d)

    chrome_options = webdriver.ChromeOptions()
    if 'headless' in d:
        chrome_options.add_argument("--headless")

    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", prefs)
    if 'headless' in d:
        chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=constants.CHROME_DRIVER_PATH)
    driver.get("https://google.com")

    driver = login(driver)
    load_cookie(driver, '/tmp/YCTW_google_cookie')
    time.sleep(2)

    try:
        with open("data/cache.txt", 'a') as outfile:
            driver.get('https://www.youtube.com/feed/history/comment_history')

            for i in range(10):
                containers = driver.find_elements_by_id('content')
                action = ActionChains(driver)
                action.move_to_element(containers[-1]).perform()
                action.click().perform()
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            links =  driver.find_elements_by_css_selector('#contents > ytd-comment-history-entry-renderer > div.main.style-scope.ytd-comment-history-entry-renderer > yt-formatted-string.summary.style-scope.ytd-comment-history-entry-renderer > a:nth-child(2)')
            print(links)
            for link in links:
                try:
                    print(link.get_attribute('href').replace('https://',''))
                    outfile.write(link.get_attribute('href').replace('https://','')+'\n')
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)
    driver.quit()
