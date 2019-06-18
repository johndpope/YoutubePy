"""OS Modules environ method to get the setup vars from the Environment"""
# import built-in & third-party modules
import time
from math import ceil
import random
import re
# from sys import platform
# from platform import python_version
import os
# import csv
# import json
# import requests
# from selenium import webdriver
# from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains

# from pyvirtualdisplay import Display
import logging
from contextlib import contextmanager
# from copy import deepcopy
import unicodedata
from sys import exit as clean_exit
from tempfile import gettempdir

# import YoutubePy modules
# from socialcommons.clarifai_util import check_image
from .login_util import login_user
# from .settings import Settings
from socialcommons.print_log_writer import log_follower_num
from socialcommons.print_log_writer import log_following_num

from socialcommons.time_util import sleep
# from socialcommons.time_util import set_sleep_percentage
# from socialcommons.util import get_active_users
from socialcommons.util import validate_userid
from socialcommons.util import web_address_navigator
from socialcommons.util import interruption_handler
from socialcommons.util import highlight_print
# from socialcommons.util import dump_record_activity
from socialcommons.util import truncate_float
from socialcommons.util import save_account_progress
from socialcommons.util import parse_cli_args
# from .unfollow_util  import get_given_user_followers
# from .unfollow_util  import get_given_user_following
# from .unfollow_util  import unfollow
# from .unfollow_util  import unfollow_user
# from .unfollow_util  import follow_user
# from .unfollow_util  import follow_restriction
# from .unfollow_util  import dump_follow_restriction
# from .unfollow_util  import set_automated_followed_pool
# from .unfollow_util  import get_follow_requests
# from .relationship_tools import get_following
# from .relationship_tools import get_followers
# from .relationship_tools import get_unfollowers
# from .relationship_tools import get_nonfollowers
# from .relationship_tools import get_fans
# from .relationship_tools import get_mutual_following
from socialcommons.database_engine import get_database
# from socialcommons.text_analytics import text_analysis
# from socialcommons.text_analytics import yandex_supported_languages
from socialcommons.browser import set_selenium_local_session
from socialcommons.browser import close_browser
from socialcommons.file_manager import get_workspace
from socialcommons.file_manager import get_logfolder

# import exceptions
from selenium.common.exceptions import NoSuchElementException
from socialcommons.exceptions import SocialPyError
from .settings import Settings

ROW_HEIGHT = 105#TODO: ROW_HEIGHT is actuallly variable in gihub so added buffer 5 to delay the failure.
ROWS_PER_PAGE = 50

class YoutubePy:
    """Class to be instantiated to use the script"""
    def __init__(self,
                 username=None,
                 userid=None,
                 password=None,
                 nogui=False,
                 selenium_local_session=True,
                 use_firefox=False,
                 browser_profile_path=None,
                 page_delay=25,
                 show_logs=True,
                 headless_browser=False,
                 proxy_address=None,
                 proxy_chrome_extension=None,
                 proxy_port=None,
                 disable_image_load=False,
                 bypass_suspicious_attempt=False,
                 bypass_with_mobile=False,
                 multi_logs=True):

        cli_args = parse_cli_args()
        username = cli_args.username or username
        userid = cli_args.userid or userid
        password = cli_args.password or password
        use_firefox = cli_args.use_firefox or use_firefox
        page_delay = cli_args.page_delay or page_delay
        headless_browser = cli_args.headless_browser or headless_browser
        proxy_address = cli_args.proxy_address or proxy_address
        proxy_port = cli_args.proxy_port or proxy_port
        disable_image_load = cli_args.disable_image_load or disable_image_load
        bypass_suspicious_attempt = (
            cli_args.bypass_suspicious_attempt or bypass_suspicious_attempt)
        bypass_with_mobile = cli_args.bypass_with_mobile or bypass_with_mobile

        if not get_workspace(Settings):
            raise SocialPyError(
                "Oh no! I don't have a workspace to work at :'(")

        self.nogui = nogui
        if nogui:
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()

        self.browser = None
        self.headless_browser = headless_browser
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self.proxy_chrome_extension = proxy_chrome_extension
        self.selenium_local_session = selenium_local_session
        self.bypass_suspicious_attempt = bypass_suspicious_attempt
        self.bypass_with_mobile = bypass_with_mobile
        self.disable_image_load = disable_image_load

        self.username = username or os.environ.get('GITHUB_USER')
        self.password = password or os.environ.get('GITHUB_PW')

        self.userid = userid
        if not self.userid:
            self.userid = self.username.split('@')[0]

        Settings.profile["name"] = self.username

        self.page_delay = page_delay
        self.switch_language = True
        self.use_firefox = use_firefox
        Settings.use_firefox = self.use_firefox
        self.browser_profile_path = browser_profile_path

        self.do_comment = False
        self.comment_percentage = 0
        self.comments = ['Cool!', 'Nice!', 'Looks good!']
        self.photo_comments = []
        self.video_comments = []

        self.do_reply_to_comments = False
        self.reply_to_comments_percent = 0
        self.comment_replies = []
        self.photo_comment_replies = []
        self.video_comment_replies = []

        self.liked_img = 0
        self.already_liked = 0
        self.liked_comments = 0
        self.commented = 0
        self.replied_to_comments = 0
        self.followed = 0
        self.already_followed = 0
        self.unfollowed = 0
        self.followed_by = 0
        self.following_num = 0
        self.inap_img = 0
        self.not_valid_users = 0
        self.video_played = 0
        self.already_Visited = 0

        self.follow_times = 1
        self.do_follow = False
        self.follow_percentage = 0
        self.dont_include = set()
        self.white_list = set()
        self.blacklist = {'enabled': 'True', 'campaign': ''}
        self.automatedFollowedPool = {"all": [], "eligible": []}
        self.do_like = False
        self.like_percentage = 0
        self.smart_hashtags = []

        self.dont_like = ['sex', 'nsfw']
        self.mandatory_words = []
        self.ignore_if_contains = []
        self.ignore_users = []

        self.user_interact_amount = 0
        self.user_interact_media = None
        self.user_interact_percentage = 0
        self.user_interact_random = False
        self.dont_follow_inap_post = True

        self.use_clarifai = False
        self.clarifai_api_key = None
        self.clarifai_models = []
        self.clarifai_workflow = []
        self.clarifai_probability = 0.50
        self.clarifai_img_tags = []
        self.clarifai_img_tags_skip = []
        self.clarifai_full_match = False
        self.clarifai_check_video = False
        self.clarifai_proxy = None

        self.potency_ratio = None   # 1.3466
        self.delimit_by_numbers = None

        self.max_followers = None   # 90000
        self.max_following = None   # 66834
        self.min_followers = None   # 35
        self.min_following = None   # 27

        self.delimit_liking = False
        self.liking_approved = True
        self.max_likes = 1000
        self.min_likes = 0

        self.delimit_commenting = False
        self.commenting_approved = True
        self.max_comments = 35
        self.min_comments = 0
        self.comments_mandatory_words = []
        self.max_posts = None
        self.min_posts = None
        self.skip_business_categories = []
        self.dont_skip_business_categories = []
        self.skip_business = False
        self.skip_no_profile_pic = False
        self.skip_private = True
        self.skip_business_percentage = 100
        self.skip_no_profile_pic_percentage = 100
        self.skip_private_percentage = 100

        self.relationship_data = {
            username: {"all_following": [], "all_followers": []}}

        self.simulation = {"enabled": True, "percentage": 100}

        self.mandatory_language = False
        self.mandatory_character = []
        self.check_letters = {}

        # use this variable to terminate the nested loops after quotient
        # reaches
        self.quotient_breach = False
        # hold the consecutive jumps and set max of it used with QS to break
        # loops
        self.jumps = {"consequent": {"likes": 0, "comments": 0, "follows": 0,
                                     "unfollows": 0},
                      "limit": {"likes": 7, "comments": 3, "follows": 5,
                                "unfollows": 4}}

        # stores the features' name which are being used by other features
        self.internal_usage = {}

        if (
                self.proxy_address and self.proxy_port > 0) or \
                self.proxy_chrome_extension:
            Settings.connection_type = "proxy"

        self.aborting = False
        self.start_time = time.time()

        # assign logger
        self.show_logs = show_logs
        Settings.show_logs = show_logs or None
        self.multi_logs = multi_logs
        self.logfolder = get_logfolder(self.username, self.multi_logs, Settings)
        self.logger = self.get_youtubepy_logger(self.show_logs)

        get_database(Settings, make=True)  # IMPORTANT: think twice before relocating

        if self.selenium_local_session is True:
            self.set_selenium_local_session(Settings)

    def get_youtubepy_logger(self, show_logs):
        """
        Handles the creation and retrieval of loggers to avoid
        re-instantiation.
        """

        existing_logger = Settings.loggers.get(self.username)
        if existing_logger is not None:
            return existing_logger
        else:
            # initialize and setup logging system for the YoutubePy object
            logger = logging.getLogger(self.username)
            logger.setLevel(logging.DEBUG)
            file_handler = logging.FileHandler(
                '{}general.log'.format(self.logfolder))
            file_handler.setLevel(logging.DEBUG)
            extra = {"username": self.username}
            logger_formatter = logging.Formatter(
                '%(levelname)s [%(asctime)s] [%(username)s]  %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(logger_formatter)
            logger.addHandler(file_handler)

            if show_logs is True:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                console_handler.setFormatter(logger_formatter)
                logger.addHandler(console_handler)

            logger = logging.LoggerAdapter(logger, extra)

            Settings.loggers[self.username] = logger
            Settings.logger = logger
            return logger

    def set_selenium_local_session(self, Settings):
        self.browser, err_msg = \
            set_selenium_local_session(self.proxy_address,
                                       self.proxy_port,
                                       self.proxy_chrome_extension,
                                       self.headless_browser,
                                       self.use_firefox,
                                       self.browser_profile_path,
                                       # Replaces
                                       # browser User
                                       # Agent from
                                       # "HeadlessChrome".
                                       self.disable_image_load,
                                       self.page_delay,
                                       self.logger,
                                       Settings)
        if len(err_msg) > 0:
            raise SocialPyError(err_msg)

    def login(self):
        """Used to login the user either with the username and password"""
        if not login_user(self.browser,
                          self.username,
                          self.userid,
                          self.password,
                          self.logger,
                          self.logfolder,
                          self.switch_language,
                          self.bypass_suspicious_attempt,
                          self.bypass_with_mobile):
            message = "Wrong login data!"
            highlight_print(Settings, self.username,
                            message,
                            "login",
                            "critical",
                            self.logger)

            return False

        else:
            message = "Logged in successfully!"
            highlight_print(Settings, self.username,
                            message,
                            "login",
                            "info",
                            self.logger)
            # try to save account progress
            try:
                save_account_progress(self.browser,
                                    "https://www.youtube.com/",
                                    self.username,
                                    self.logger)
            except Exception:
                self.logger.warning(
                    'Unable to save account progress, skipping data update')

        self.followed_by = log_follower_num(self.browser,
                                            Settings,
                                            "https://www.youtube.com/",
                                            self.username,
                                            self.userid,
                                            self.logfolder)

        self.following_num = log_following_num(self.browser,
                                            Settings,
                                            "https://www.youtube.com/",
                                            self.username,
                                            self.userid,
                                            self.logfolder)

        return self

    def set_do_follow(self, enabled=False, percentage=0, times=1):
        """Defines if the user of the liked image should be followed"""
        if self.aborting:
            return self

        self.follow_times = times
        self.do_follow = enabled
        self.follow_percentage = percentage

        return self

    def set_dont_include(self, friends=None):
        """Defines which accounts should not be unfollowed"""
        if self.aborting:
            return self

        self.dont_include = set(friends) or set()
        self.white_list = set(friends) or set()

        return self

    def validate_user_call(self, user_name):
        """ Short call of validate_userid() function """
        validation, details = \
            validate_userid(self.browser,
                            "https://youtube.com/",
                            user_name,
                            self.username,
                            self.userid,
                            self.ignore_users,
                            self.blacklist,
                            self.potency_ratio,
                            self.delimit_by_numbers,
                            self.max_followers,
                            self.max_following,
                            self.min_followers,
                            self.min_following,
                            self.min_posts,
                            self.max_posts,
                            self.skip_private,
                            self.skip_private_percentage,
                            self.skip_no_profile_pic,
                            self.skip_no_profile_pic_percentage,
                            self.skip_business,
                            self.skip_business_percentage,
                            self.skip_business_categories,
                            self.dont_skip_business_categories,
                            self.logger,
                            self.logfolder, Settings)
        return validation, details

    def fetch_smart_comments(self, is_video, temp_comments):
        if temp_comments:
            # Use clarifai related comments only!
            comments = temp_comments
        elif is_video:
            comments = (self.comments +
                        self.video_comments)
        else:
            comments = (self.comments +
                        self.photo_comments)

        return comments

    def prepare_comment(self, textdata):
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

    def search_and_comment(self, query):
        print('fetching latest list')
        with open(f'data/youtube_giveaway_commentlinks.txt', 'a') as outfile:
            try:
                self.browser.get("https://www.youtube.com/results?sp=CAISBAgCEAE%253D&search_query={}".format(query))
                for i in range(50):
                    time.sleep(2)
                    self.browser.execute_script("window.scrollTo(0," + str(i*500) + ");")
                links = self.browser.find_elements_by_css_selector('a#video-title')
                for link in links:
                    print(link.get_attribute('href'))
                    outfile.write(link.get_attribute('href') + '\n')
            except Exception as e:
                print(e)

        cache_arr = []
        print('loading cache')
        with open(f'data/cache.txt') as infile:
            for url in infile:
                cache_arr.append(url)

        with open(f'data/youtube_giveaway_commentlinks.txt') as infile:
            ctr = 0
            for url in infile:
                try:
                    if url in cache_arr:
                        print("ALREADY COMMENTED", url)
                    else:
                        url = url.replace('\n','')
                        print("====", url, "====")
                        self.browser.get(url)

                        self.browser.execute_script("window.scrollTo(0, 50)")
                        time.sleep(4)

                        try:
                            like_button =  self.browser.find_element_by_xpath('//*[@id="top-level-buttons"]/ytd-toggle-button-renderer[1]/a/yt-icon-button')#[@aria-pressed="false"]')
                            if like_button:
                                like_button.click()
                                time.sleep(2)
                        except Exception as e:
                            print(e)

                        for i in range(10):
                            time.sleep(2)
                            self.browser.execute_script("window.scrollTo(0, 450)")

                        try:
                            subscribe_button =  self.browser.find_element_by_xpath('//*[@id="subscribe-button"]/ytd-subscribe-button-renderer')#/paper-button')#/yt-formatted-string')
                            if subscribe_button and subscribe_button.text.split(' ')[0].strip().lower() == 'subscribe':
                                subscribe_button.click()
                                time.sleep(2)
                        except Exception as e:
                            print(e)

                        description_element = self.browser.find_element_by_xpath('//*[@id="description"]')
                        comment = self.prepare_comment(description_element.text)

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

    def end(self):
        """Closes the current session"""
        close_browser(self.browser, False, self.logger)

        with interruption_handler():
            # close virtual display
            if self.nogui:
                self.display.stop()

            # write useful information
            # dump_follow_restriction(self.username,
            #                         self.logger,
            #                         self.logfolder)
            # dump_record_activity(self.username,
            #                      self.logger,
            #                      self.logfolder,
            #                      Settings)

            with open('{}followed.txt'.format(self.logfolder), 'w') \
                    as followFile:
                followFile.write(str(self.followed))

            # output live stats before leaving
            self.live_report()

            message = "Session ended!"
            highlight_print(Settings, self.username, message, "end", "info", self.logger)
            print("\n\n")

    @contextmanager
    def feature_in_feature(self, feature, validate_users):
        """
         Use once a host feature calls a guest
        feature WHERE guest needs special behaviour(s)
        """
        try:
            # add the guest which is gonna be used by the host :)
            self.internal_usage[feature] = {"validate": validate_users}
            yield

        finally:
            # remove the guest just after using it
            self.internal_usage.pop(feature)

    def live_report(self):
        """ Report live sessional statistics """

        print('')

        stats = [self.liked_img, self.already_liked,
                 self.commented,
                 self.followed, self.already_followed,
                 self.unfollowed,
                 self.inap_img,
                 self.not_valid_users]

        if self.following_num and self.followed_by:
            owner_relationship_info = (
                "On session start was FOLLOWING {} users"
                " & had {} FOLLOWERS"
                .format(self.following_num,
                        self.followed_by))
        else:
            owner_relationship_info = ''

        sessional_run_time = self.run_time()
        run_time_info = ("{} seconds".format(sessional_run_time) if
                         sessional_run_time < 60 else
                         "{} minutes".format(truncate_float(
                             sessional_run_time / 60, 2)) if
                         sessional_run_time < 3600 else
                         "{} hours".format(truncate_float(
                             sessional_run_time / 60 / 60, 2)))
        run_time_msg = "[Session lasted {}]".format(run_time_info)

        if any(stat for stat in stats):
            self.logger.info(
                "Sessional Live Report:\n"
                "\t|> LIKED {} images  |  ALREADY LIKED: {}\n"
                "\t|> COMMENTED on {} images\n"
                "\t|> FOLLOWED {} users  |  ALREADY FOLLOWED: {}\n"
                "\t|> UNFOLLOWED {} users\n"
                "\t|> LIKED {} comments\n"
                "\t|> REPLIED to {} comments\n"
                "\t|> INAPPROPRIATE images: {}\n"
                "\t|> NOT VALID users: {}\n"
                "\n{}\n{}"
                .format(self.liked_img,
                        self.already_liked,
                        self.commented,
                        self.followed,
                        self.already_followed,
                        self.unfollowed,
                        self.liked_comments,
                        self.replied_to_comments,
                        self.inap_img,
                        self.not_valid_users,
                        owner_relationship_info,
                        run_time_msg))
        else:
            self.logger.info("Sessional Live Report:\n"
                             "\t|> No any statistics to show\n"
                             "\n{}\n{}"
                             .format(owner_relationship_info,
                                     run_time_msg))

    def is_mandatory_character(self, uchr):
        if self.aborting:
            return self
        try:
            return self.check_letters[uchr]
        except KeyError:
            return self.check_letters.setdefault(uchr,
                                                 self.mandatory_character in
                                                 unicodedata.name(uchr))

    def run_time(self):
        """ Get the time session lasted in seconds """

        real_time = time.time()
        run_time = (real_time - self.start_time)
        run_time = truncate_float(run_time, 2)

        return run_time

    def check_character_set(self, unistr):
        self.check_letters = {}
        if self.aborting:
            return self
        return all(self.is_mandatory_character(uchr)
                   for uchr in unistr
                   if uchr.isalpha())

@contextmanager
def smart_run(session):
    try:
        if session.login():
            yield
        else:
            print("Not proceeding as login failed")

    except (Exception, KeyboardInterrupt) as exc:
        if isinstance(exc, NoSuchElementException):
            # the problem is with a change in IG page layout
            log_file = "{}.html".format(time.strftime("%Y%m%d-%H%M%S"))
            file_path = os.path.join(gettempdir(), log_file)
            with open(file_path, "wb") as fp:
                fp.write(session.browser.page_source.encode("utf-8"))
            print("{0}\nIf raising an issue, "
                  "please also upload the file located at:\n{1}\n{0}"
                  .format('*' * 70, file_path))

        # provide full stacktrace (else than external interrupt)
        if isinstance(exc, KeyboardInterrupt):
            clean_exit("You have exited successfully.")
        else:
            raise

    finally:
        session.end()
