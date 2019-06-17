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
from pip._vendor.distlib.util import proceed

from urllib.request import Request, urlopen

def load_cookie(driver, path):
    with open(path, 'rb') as cookies_file:
        cookies = pickle.load(cookies_file)
        for cookie in cookies:
            driver.add_cookie(cookie)

def get_time():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

def prepare_comment(textdata):
    comment = "i liked, subscribed and want to be eligible for the giveaway"
    lasthalf = textdata.lower().split('commenting ')
    if len(lasthalf) == 1:
        lasthalf = textdata.lower().split('comment ')
    if len(lasthalf) >= 2:
        comment = lasthalf[1]
        firstcommentline = comment.split('\n')
        if len(firstcommentline) >= 2:
            comment = firstcommentline[0]
        firstcomment = comment.split('.')
        if len(firstcomment) >= 2:
            comment = firstcomment[0]
    quotes_arr = re.findall('"([^"]*)"', comment)
    if len(quotes_arr) > 0 and len(quotes_arr[0]) >= 4:
        comment = quotes_arr[0]
    else:
        comment = comment.replace('why', 'because i love your contents')
        comment = comment.replace('your', 'my')
        comment = comment.replace('you', 'me')
        comment = comment.replace('username', 'username:ishandutta2007')
        if 'instagram id' in comment:
            comment = comment.replace('instagram id', 'instagram id:dutta.ishan')
        elif 'instagramid' in comment:
            comment = comment.replace('instagramid', 'instagramid:dutta.ishan')
        elif 'instagram' in comment:
            comment = comment.replace('instagram', 'instagram:dutta.ishan')
        elif 'instagram id' in textdata:
            comment = comment + '. instagram id:dutta.ishan'
        elif 'instagramid' in textdata:
            comment = comment + '. instagramid:dutta.ishan'
        elif 'instagram' in textdata:
            comment = comment + '. instagram:dutta.ishan'

        if 'fruit' in comment:
            comment = comment.replace('fruit', 'fruit:apple')
        elif 'fruit' in textdata:
            comment = comment  + '. fruit:apple'

        if 'animal' in comment:
            comment = comment.replace('animal', 'animal:tiger')
        elif 'animal' in textdata:
            comment = comment  + '. animal:tiger'
    comment = comment.strip()
    comment = comment.capitalize()
    return comment

def crawl_latest_list(driver):
    print('fetching latest list')
    with open(f'data/youtube_giveaway_commentlinks.txt', 'a') as outfile:
        try:
            driver.get("https://www.youtube.com/results?sp=CAISBAgCEAE%253D&search_query=giveaway")
            for i in range(50):
                time.sleep(2)
                driver.execute_script("window.scrollTo(0," + str(i*500) + ");")
            links = driver.find_elements_by_css_selector('a#video-title')
            for link in links:
                print(link.get_attribute('href'))
                outfile.write(link.get_attribute('href') + '\n')
        except Exception as e:
            print(e)

cache_arr = []
def load_cache():
    global cache_arr
    print('loading cache')
    with open(f'data/cache.txt') as infile:
        for url in infile:
            cache_arr.append(url)

def login(driver):
    driver.get('https://accounts.google.com/ServiceLogin?continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Fhl%3Den%26feature%3Dcomment%26app%3Ddesktop%26next%3D%252Fall_comments%253Fv%253DLAr6oAKieHk%26action_handle_signin%3Dtrue&uilel=3&service=youtube&passive=true&hl=en') 

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
    crawl_latest_list(driver)
    load_cache()
    print(cache_arr)

    with open(f'data/youtube_giveaway_commentlinks.txt') as infile:
        ctr = 0
        for url in infile:
            try:
                if url in cache_arr:
                    print("ALREADY COMMENTED", url)
                else:
                    url = url.replace('\n','')
                    print("====", url, "====")
                    driver.get(url)

                    driver.execute_script("window.scrollTo(0, 50)")
                    time.sleep(4)

                    try:
                        like_button =  driver.find_element_by_xpath('//*[@id="top-level-buttons"]/ytd-toggle-button-renderer[1]/a/yt-icon-button')#[@aria-pressed="false"]')
                        if like_button:
                            like_button.click()
                            time.sleep(2)
                    except Exception as e:
                        print(e)

                    for i in range(10):
                        time.sleep(2)
                        driver.execute_script("window.scrollTo(0, 450)")

                    try:
                        subscribe_button =  driver.find_element_by_xpath('//*[@id="subscribe-button"]/ytd-subscribe-button-renderer')#/paper-button')#/yt-formatted-string')
                        if subscribe_button and subscribe_button.text.split(' ')[0].strip().lower() == 'subscribe':
                            subscribe_button.click()
                            time.sleep(2)
                    except Exception as e:
                        print(e)

                    description_element = driver.find_element_by_xpath('//*[@id="description"]')
                    comment = prepare_comment(description_element.text)

                    box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "simple-box")))
                    box.click()

                    comm_dia = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'comment-dialog')))
                    action = ActionChains(driver)
                    action.move_to_element(comm_dia).perform()
                    action.click().perform()

                    textarea = WebDriverWait(comm_dia, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.textarea-container > textarea#textarea")))
                    textarea.send_keys(comment)
                    time.sleep(2)

                    submit_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'submit-button')))
                    action = ActionChains(driver)
                    action.move_to_element(submit_button).perform()
                    action.click().perform()
                    time.sleep(2)
                    with open(f'data/cache.txt', 'a') as outfile:
                        outfile.write('https://' + url + '\n')
            except Exception as e:
                print(e)
            ctr = ctr + 1
    driver.quit()
