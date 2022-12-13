import unittest
from utils.database import InstagramDatabase

from dotenv import load_dotenv
load_dotenv()
import os

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from utils.instagram_crawler import InstagramCrawler, get_selector
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import config
from time import sleep

class TestHelper():

    def check_element_selector(self, Tester, checking_function, ready_selector, config_selector, msg="element"):
        """Check if selector is valid by a given checking_function (usually driver.find_element) and catch NoSuchElementExceptions to then make the test fail.

        Args:
            Tester (unittest.TestCase): The ongoing test case to potentially fail.
            checking_function (Function): The callable function to test the selector.
            ready_selector (tuple of selector and query): The selector with its query to be tested to find an element.
            config_selector (string): The selector as it stands in config.py
            msg (str, optional): _description_. Defaults to "element".

        Returns:
            WebElement: Returns the found WebElement
        """
        try:
            return checking_function(*ready_selector)
        except NoSuchElementException as e:
            Tester.fail(f"Couldn't find {msg} using selector: {config_selector}.")

class TestInstagramCrawler(unittest.TestCase):

    def setUp(self): 
        self.DB = InstagramDatabase(os.getenv("DB_CONNECTION_STRING"))
        self.driver = webdriver.ChromiumEdge(service=Service(EdgeChromiumDriverManager().install()))
        self.InstagramCrawler = InstagramCrawler(self.driver, self.DB)
        self.TestHelper = TestHelper()

    def tearDown(self): self.InstagramCrawler.driver.quit()

    def test_selectors(self):

        # check if driver works and goes to correct url
        try:
            self.InstagramCrawler.go_to_base_url()
        except Exception as e:
            self.fail(f"Couldn't start webdriver and go to base url: {e}")

        
        url = self.driver.current_url
        self.assertEqual(url, config.BASE_URL)
        sleep(3)

        # test if cookie popup selector works
        cookie_popup = self.TestHelper.check_element_selector(self, self.InstagramCrawler.driver.find_element, get_selector("COOKIE_POPUP"), config.COOKIE_POPUP, "cookie popup")
        try:
            cookie_popup.click()
            sleep(1)
        except Exception as e:
            self.fail(f"Couldn't click cookie popup: {e}")

        # test username input
        username = self.TestHelper.check_element_selector(self, self.InstagramCrawler.driver.find_element, get_selector("USERNAME_INPUT"), config.USERNAME_INPUT, "username input")
        try:
            username.send_keys(os.getenv("INSTAGRAM_USERNAME"))
        except Exception as e:
            self.fail(f"Couldn't send keys to username input: {e}")
        
        # test password input
        password = self.TestHelper.check_element_selector(self, self.InstagramCrawler.driver.find_element, get_selector("PASSWORD_INPUT"), config.PASSWORD_INPUT, "password input")
        try:
            password.send_keys(os.getenv("INSTAGRAM_PASSWORD"))
        except Exception as e:
            self.fail(f"Couldn't send keys to password input: {e}")

        # test login button
        login_button = self.TestHelper.check_element_selector(self, self.InstagramCrawler.driver.find_element, get_selector("LOGIN_BUTTON"), config.LOGIN_BUTTON, "login button")
        try:
            login_button.click()
        except Exception as e:
            self.fail(f"Couldn't click login button: {e}")

        # test if profile link is found and if selector works
        is_logged_in = self.TestHelper.check_element_selector(self, self.InstagramCrawler.wait_for_page_to_load, get_selector("PROFILE_SELECTOR"), config.PROFILE_SELECTOR, "profile link after login process")
        self.assertEqual(WebElement, type(is_logged_in))

        # go to test account page (go_to_link() should work after login procedure OK)
        self.InstagramCrawler.go_to_link(config.BASE_URL + config.TEST_ACCOUNT)

        # test if account page loads and if selector works
        self.TestHelper.check_element_selector(self, self.InstagramCrawler.wait_for_page_to_load, get_selector("WAIT_FOR_ACCOUNT_TO_LOAD", [config.TEST_ACCOUNT]), config.WAIT_FOR_ACCOUNT_TO_LOAD, "account page")

        # test if currently visible posts are found and if selector works
        currently_visible_posts = self.TestHelper.check_element_selector(self, self.InstagramCrawler.driver.find_elements, get_selector("CURRENTLY_VISIBLE_POSTS"), config.CURRENTLY_VISIBLE_POSTS, "currently visible posts")
        self.assertEqual(list, type(currently_visible_posts))
        try:
            post_link = currently_visible_posts[0].get_attribute("href")
        except Exception as e:
            self.fail(f"Couldn't get post link from currently visible post with selector {config.CURRENTLY_VISIBLE_POSTS}: {e}")

        self.InstagramCrawler.go_to_link(post_link)
        sleep(3)
        
        # test if post page loads 
        self.TestHelper.check_element_selector(self, self.InstagramCrawler.wait_for_page_to_load, get_selector("WAIT_FOR_POST_TO_LOAD"), config.WAIT_FOR_POST_TO_LOAD, "post page")

        sleep(3)

        # test if post information selectors works
        post_comment = self.TestHelper.check_element_selector(self, self.InstagramCrawler.driver.find_element, get_selector("TEST_POST_COMMENT"), config.TEST_POST_COMMENT, "post comment")
        post_likes = self.TestHelper.check_element_selector(self, self.InstagramCrawler.driver.find_element, get_selector("TEST_POST_LIKES"), config.TEST_POST_LIKES, "post likes")
        post_date = self.TestHelper.check_element_selector(self, self.InstagramCrawler.driver.find_element, get_selector("TEST_POST_DATE"), config.TEST_POST_DATE, "post date")
        load_more_comments = self.TestHelper.check_element_selector(self, self.InstagramCrawler.driver.find_element, get_selector("LOAD_MORE_COMMENTS_BUTTON"), config.LOAD_MORE_COMMENTS_BUTTON, "load more comments button")
        load_more_replies = self.TestHelper.check_element_selector(self, self.InstagramCrawler.driver.find_element, get_selector("VIEW_MORE_REPLIES_BUTTON"), config.VIEW_MORE_REPLIES_BUTTON, "load more replies button")
        comments_container = self.TestHelper.check_element_selector(self, self.InstagramCrawler.driver.find_elements, get_selector("ALL_COMMENTS_CONTAINER"), config.ALL_COMMENTS_CONTAINER, "all comments container")
        self.assertEqual(list, type(comments_container))

        #test if comment container contains comments
        comment_container = self.TestHelper.check_element_selector(self, comments_container[0].find_element, get_selector("COMMENT_CONTAINER"), config.COMMENT_CONTAINER, "comment container")
        comment_text = self.TestHelper.check_element_selector(self, comment_container.find_element, get_selector("COMMENT_TEXT"), config.COMMENT_TEXT, "comment text")
        comment_owner = self.TestHelper.check_element_selector(self, comment_container.find_element, get_selector("COMMENT_OWNER"), config.COMMENT_OWNER, "comment owner")
        comment_likes = self.TestHelper.check_element_selector(self, comment_container.find_element, get_selector("COMMENT_LIKES"), config.COMMENT_LIKES, "comment likes")
        comment_date = self.TestHelper.check_element_selector(self, comment_container.find_element, get_selector("COMMENT_DATE"), config.COMMENT_DATE, "comment date")

        # test if replies to comment selectors work (test account needs to be setup properly like mentioned in "Running the tests" in Readme.md)
        replies_to_comment_container = []
        replies_to_comment_container = self.TestHelper.check_element_selector(self, comments_container[0].find_elements, get_selector("REPLIES_TO_COMMENT_CONTAINER"), config.REPLIES_TO_COMMENT_CONTAINER, "replies to comment container")
        self.assertEqual(list, type(replies_to_comment_container))

        # check if loading more replies works
        replies_to_comment_container_length = len(replies_to_comment_container)
        load_more_replies.click()
        sleep(3)
        replies_to_comment_container_after_click = self.TestHelper.check_element_selector(self, comments_container[0].find_elements, get_selector("REPLIES_TO_COMMENT_CONTAINER"), config.REPLIES_TO_COMMENT_CONTAINER, "replies to comment container")
        replies_to_comment_container_length_after_click = len(replies_to_comment_container_after_click)
        self.assertGreater(replies_to_comment_container_length_after_click, replies_to_comment_container_length)

        # check if replies to comment selectors work
        reply_text = self.TestHelper.check_element_selector(self, replies_to_comment_container_after_click[0].find_element, get_selector("REPLY_TEXT"), config.REPLY_TEXT, "reply text")
        teply_owner = self.TestHelper.check_element_selector(self, replies_to_comment_container_after_click[0].find_element, get_selector("REPLY_OWNER"), config.REPLY_OWNER, "reply owner")
        reply_likes = self.TestHelper.check_element_selector(self, replies_to_comment_container_after_click[0].find_element, get_selector("REPLY_LIKES"), config.REPLY_LIKES, "reply likes")
        reply_date = self.TestHelper.check_element_selector(self, replies_to_comment_container_after_click[0].find_element, get_selector("REPLY_DATE"), config.REPLY_DATE, "reply date")

        #check if retrieving datetimes work
        try:
            post_date = post_date.get_attribute("datetime")
        except Exception as e:
            self.fail(f"Couldn't get attribute 'datetime' from post date element with selector {config.TEST_POST_DATE}: {e}")
        try:
            comment_date = comment_date.get_attribute("datetime")
        except Exception as e:
            self.fail(f"Couldn't get attribute 'datetime' from post date element with selector {config.COMMENT_DATE}: {e}")
        try:
            reply_date = reply_date.get_attribute("datetime")
        except Exception as e:
            self.fail(f"Couldn't get attribute 'datetime' from post date element with selector {config.COMMENT_DATE}: {e}")

        #check if loading more comments works
        comments_container_length = len(comments_container)
        load_more_comments.click()
        sleep(3)
        comments_container_after_click = self.TestHelper.check_element_selector(self, self.InstagramCrawler.driver.find_elements, get_selector("ALL_COMMENTS_CONTAINER"), config.COMMENT_CONTAINER, "comment container")
        comments_container_length_after_click = len(comments_container_after_click)
        self.assertGreater(comments_container_length_after_click, comments_container_length)