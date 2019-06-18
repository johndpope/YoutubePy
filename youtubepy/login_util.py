"""Module only used for the login part of the script"""
# import built-in & third-party modules
import time
import pickle
from selenium.webdriver.common.action_chains import ActionChains

# import YoutubePy modules
from socialcommons.time_util import sleep
from socialcommons.util import update_activity
from socialcommons.util import web_address_navigator
from socialcommons.util import reload_webpage
from socialcommons.util import click_element
from socialcommons.util import explicit_wait
# from socialcommons.util import check_authorization
from .settings import Settings

# import exceptions
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys

def login_user(browser,
               username,
               userid,
               password,
               logger,
               logfolder,
               switch_language=True,
               bypass_suspicious_attempt=False,
               bypass_with_mobile=False):
    """Logins the user with the given username and password"""
    assert username, 'Username not provided'
    assert password, 'Password not provided'

    print(username, password)
    ig_homepage = "https://accounts.google.com/ServiceLogin?continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Fhl%3Den%26feature%3Dcomment%26app%3Ddesktop%26next%3D%252Fall_comments%253Fv%253DLAr6oAKieHk%26action_handle_signin%3Dtrue&uilel=3&service=youtube&passive=true&hl=en"
    web_address_navigator( browser, ig_homepage, Settings)
    cookie_loaded = False

    # try to load cookie from username
    try:
        for cookie in pickle.load(open('{0}{1}_cookie.pkl'
                                       .format(logfolder, username), 'rb')):
            browser.add_cookie(cookie)
            cookie_loaded = True
    except (WebDriverException, OSError, IOError):
        print("Cookie file not found, creating cookie...")

    # include time.sleep(1) to prevent getting stuck on google.com
    time.sleep(1)

    web_address_navigator(browser, ig_homepage, Settings)
    reload_webpage(browser, Settings)

    # try:
    #     profile_pic = browser.find_element_by_xpath('//header/div[8]/details/summary/img')
    #     if profile_pic:
    #         login_state = True
    #     else:
    #         login_state = False
    # except Exception as e:
    #     print(e)
    #     login_state = False

    # print('login_state:', login_state)

    # if login_state is True:
    #     # dismiss_notification_offer(browser, logger)
    #     return True

    # if user is still not logged in, then there is an issue with the cookie
    # so go create a new cookie..
    if cookie_loaded:
        print("Issue with cookie for user {}. Creating "
              "new cookie...".format(username))

    # wait until the 'username' input element is located and visible
    input_username_XP = '//*[@id="identifierId"]'
    # explicit_wait(browser, "VOEL", [input_username_XP, "XPath"], logger)

    input_username = browser.find_element_by_xpath(input_username_XP)

    print('moving to input_username')
    print('entering input_username')
    (ActionChains(browser)
     .move_to_element(input_username)
     .click()
     .send_keys(username)
     .perform())

    sleep(1)

    (ActionChains(browser)
     .send_keys(Keys.ENTER)
     .perform())
    # update server calls for both 'click' and 'send_keys' actions
    for i in range(2):
        update_activity(Settings)

    sleep(1)

    #  password
    input_password = browser.find_elements_by_xpath("//*[@id='password']/div[1]/div/div[1]/input")
    if not isinstance(password, str):
        password = str(password)

    print('entering input_password')
    (ActionChains(browser)
     .move_to_element(input_password[0])
     .click()
     .send_keys(password)
     .perform())

    sleep(1)

    (ActionChains(browser)
     .send_keys(Keys.ENTER)
     .perform())
    # update server calls for both 'click' and 'send_keys' actions
    for i in range(2):
        update_activity(Settings)

    sleep(1)

    print('submitting (ie just pres enter)')
    (ActionChains(browser)
     .send_keys(Keys.ENTER)
     .perform())
 
    # update server calls
    update_activity(Settings)

    sleep(1)

    # wait until page fully load
    explicit_wait(browser, "PFL", [], logger, 5)

    try:
        profile_pic = browser.find_element_by_xpath('//*[@id="img"]')        
        if profile_pic:
            login_state = True
            print('logged in')
            pickle.dump(browser.get_cookies(), open(
                '{0}{1}_cookie.pkl'.format(logfolder, username), 'wb'))
        else:
            login_state = False
    except Exception as e:
        print(e)
        login_state = False
    
    return login_state

