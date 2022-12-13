from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

import os
import uuid
import pandas as pd
from time import sleep
import time
from datetime import datetime
import config
from dotenv import load_dotenv
load_dotenv("../")

def get_selector(ENV_VAR_NAME, variables_to_inject = []):
    """Returns a selenium.webdriver.common.by.By selector and a query string for that selector

    Args:
        ENV_VAR_NAME (string): name of the environment variable in format "selector,query"
        variables_to_inject (list, optional): injects the variables into the environment variable where there is an empty curly bracket {}. Defaults to [].

    Returns:
        tuple: returns a parsed selenium.webdriver.common.by.By selector and query string
    """

    selector, query = getattr(config, ENV_VAR_NAME).split(",", maxsplit = 1)
    if len(variables_to_inject) > 0:
        query = query.format(*variables_to_inject)
    selector = getattr(By, selector)
    return selector, query

class InstagramCrawler():
    """Class to crawl an account's posts and a post's comments.
    """

    def __init__(self, driver, DB):
        """Instantiates a new instance of InstagramCrawler. Sets the driver and DB. InstagramCrawler has two additional
        attributes: A dictionary of posts that is filled during execution of the get_all_posts() method.

        Args:
            driver (selenium.webdriver): Selenium webdriver object used to interact with the instagram webpage.
            DB (database object): Database object used to store data.
        """
        self.driver = driver
        self.posts = {}
        self.DB = DB

    def go_to_link(self, url): 
        """Sets the webdriver to the specified URL.

        Args:
            url (string): Url to go to.
        """
        self.driver.get(url)

    def go_to_base_url(self): 
        """Sets the webdriver url to the base url specified in the config file.
        """
        self.driver.get(config.BASE_URL)

    def refresh_crawler(self, logged_in = False):
        """Sets the crawler to the base url, logs in if needed, bypasses notifitcation popup

        Args:
            logged_in (bool, optional): If True, ignores potential login form if driver has already logged in. Defaults to False.
        """
        self.go_to_base_url()
        if not logged_in:
            self.bypass_cookie_popup()
            self.login()

        #check if logged in successfully
        try: 
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((get_selector("PROFILE_SELECTOR"))))
        except TimeoutException as e:
            print("Error while trying to login: ", e)

        #wait if notification popup appears, randomly appears sometimes 
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((get_selector("NOTIFICATION_POPUP")))).click()
        except: pass

    def bypass_cookie_popup(self):
        """Waits for a potential cookie popup to appear and tries to bypass it using the selector specified in the COOKIE_POPUP variable in config.py.
        """
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((get_selector("COOKIE_POPUP")))).click()
        except Exception as e:
            print("Exception while trying to close cookie window: ", e)

    def login(self):
        """Waits for login form to appear and tries to login using environment variables INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD.
        """
        sleep(1)
        try:
            username = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username.send_keys(os.getenv("INSTAGRAM_USERNAME"))
            self.driver.find_element(By.NAME, "password").send_keys(os.getenv("INSTAGRAM_PASSWORD"))
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        except NoSuchElementException as e:
            print("Couldn't find element: ", e)
        except TimeoutException as e:
            print("Couldn't find element: ", e)
        except Exception as e:
            print("Unknown exception occurred in login(): ", e)

    def search_account(self, account_name):
        """Searches for an account using the Instagram search engine. Returns a list of account links.

        Args:
            account_name (string): Text used in search bar.

        Returns:
            list of strings: List of urls to accounts that appeared in search result.
        """
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((get_selector("SEARCH_ICON")))).click()
            search = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((get_selector("SEARCH_INPUT"))))
            search.send_keys(account_name)
            
            # potential to click on matching account
            search_results = self.driver.find_elements(*get_selector("SEARCH_RESULTS"))
            urls = []
            for s in search_results:
                urls.append(s.get_attribute("href"))
            return urls
        except Exception as e:
            print("Exception while searching for an account through the search bar: ", e)

    def get_all_posts(self, account_name): 
        """SCrolls through account page given by the account_name parameter and returns all post urls of that account as soon as the end of the page is reached.

        Args:
            account_name (string): The account to be crawled through.

        Returns:
            dict: Returns a dictionary with key;value pairs of the selenium object ids of the post links and the corresponding post url.
        """

        self.refresh_crawler()
        self.go_to_link(config.BASE_URL + account_name)
        # wait till account page is loaded
        self.wait_for_page_to_load(*get_selector("WAIT_FOR_ACCOUNT_TO_LOAD", [account_name]))
        sleep(1)

        # https://stackoverflow.com/questions/44721009/how-to-check-if-further-scroll-down-is-not-possible-using-selenium
        reached_page_end = False

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while not reached_page_end:
            self.driver.find_element(By.XPATH, '//body').send_keys(Keys.END)   
            time.sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if last_height == new_height:
                reached_page_end = True
            else:
                last_height = new_height
            
            #get currently visible posts
            for post in self.driver.find_elements(*get_selector("CURRENTLY_VISIBLE_POSTS")):
                self.posts[post.__dict__["_id"]] = post.get_attribute("href")
        
        return self.posts

    def load_all_comments(self, selector:object, query:str):
        """Loads all the comments of a post until no "View more comments" button is clickable.

        Args:
            selector (selenium.webdriver.common.by.By object): Selector to find the "View more comments" button.
            query (string): Query for the selector.
        """
        i = 0
        while True:
            try:
                sleep(1)
                self.driver.implicitly_wait(0)
                WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((selector, query))).click()
                self.driver.implicitly_wait(3)
                i += 1
                sleep(3)
            except TimeoutException as e: 
                print(f"Done Loading Comments {i} times")
                return
            except Exception as e:
                print("Exception thrown whie loading more comments: ", e)

    def load_all_comment_replies(self, selector:object, query:str):
        """Iteratively loads all replies in a set of comments. A post can have multiple "View more replies" buttons. This function clicks on all of them in a loop until no more "View more replies" buttons are clickable.

        Args:
            selector (selenium.webdriver.common.by.By object): Selector to find the "View more replies" buttons.
            query (string): Query for the selector.
        """
        i = 0
        while True:
            try: 
                self.driver.implicitly_wait(0)
                WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((selector, query))).click()
                self.driver.implicitly_wait(3)
                sleep(1)
                i+=1
            except TimeoutException as e: 
                print(f"Done Loading Replies {i} times")
                return
            except NoSuchElementException as e:
                print(f"Done Loading Replies {i} times")
                return
            except Exception as e:
                print("Exception thrown whie loading more replies: ", e)
                return
        
    def wait_for_page_to_load(self, selector:object, query:str, seconds = 10):
        """Waits for page to load given the selector and query string. Default is a wait time of 10 seconds.

        Args:
            selector (selenium.webdriver.common.by.By object): Selector to find the element.
            query (string): Query for the selector.
            seconds (int, optional): Seconds to wait until exception is raised. Defaults to 10.
        """
        element = WebDriverWait(self.driver, seconds).until(
            EC.presence_of_element_located((selector, query))
        )
        return element

    def view_hidden_comments(self):
        """If loading all comments of a post reaches the end, there might be some hidden comments that Instagram hides from the user because of different reasons. 
        Ignores the timout error if no hidden comments are available to load.
        """
        try:
            self.driver.implicitly_wait(0)
            WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable(get_selector("HIDDEN_COMMENTS"))).click()
            self.driver.implicitly_wait(3)
        except TimeoutException: return
        except Exception as e: 
            print(e)
            return

    def find_element_with_possible_exception(self, driver, selector, query):
        """Finds an element and if it's not found, catches/ignores the timeout error.

        Args:
            selector (selenium.webdriver.common.by.By object): Selector to find the element.
            query (string): Query for the selector.

        Returns:
            selenium WebElement object: Returns None if the element is not found. 
        """
        try:
            return driver.find_element(selector, query)
        except TimeoutException: return None
        except NoSuchElementException: return None
        except Exception as e:
            print(e)
            return None

    def add_post_comment_to_DB(self, post_url, replies_count, account_name):
        #TODO: put into 2 functions: get_post_info and add_new_entry_to_DB, maybe put all of this into "DB.add_entry"
        """Crawls post information then builds a post entry for the database. Add it to the database using a generated unique identifier.

        Args:
            post_url (string): The post url to be added to the database.
            replies_count (int): The number of replies to the post.
            account_name (string): The account name for the post entry.

        Returns:
            string: Returns the unique identifier used to add the post to the database.
        """

        post_comment = self.find_element_with_possible_exception(self.driver, *get_selector("POST_COMMENT"))
        post_likes = self.find_element_with_possible_exception(self.driver, *get_selector("POST_LIKES"))
        post_date = self.find_element_with_possible_exception(self.driver, *get_selector("POST_DATE"))

        if post_comment != None: post_comment = post_comment.text
        if post_likes != None: post_likes = post_likes.text
        if post_date != None: post_date = post_date.get_attribute("datetime")

        post_entry = pd.Series({
            "post_url": post_url,
            "is_post": True,
            "commenter": account_name,
            "text": post_comment,
            "replies_to": None,
            "replies_count": replies_count,
            "likes": post_likes,
            "date": post_date,
            "crawl_time": datetime.now()
        })
        post_uuid = uuid.uuid4()
        self.DB.add_entry(post_uuid, post_entry)

        #Notify user if any of the post info is missing
        if any([post_comment == None, post_likes == None, post_date == None]):
            print(f"Post info not complete in post {post_url}: \npost comment: {post_comment}\npost likes: {post_likes} \npost date: {post_date}")

        return post_uuid

    def add_normal_comment_to_DB(self):
        pass

    def add_reply_to_comment_to_DB(self):
        pass

    def crawl_post(self, post_url, account_name):
        """Crawls the post specified by the post_url parameter. Crawls through post specific data, all the comments and all their potential replies. Saves all the data in the database attribute of the InstagramCrawler class.

        Args:
            post_url (string): Url of the post to be crawled.
            account_name (string): Account name of the post to be crawled. Used for checking data on the webpage. 

        Returns:
            string: Returns the post url used.
        """

        self.go_to_link(post_url)
        self.wait_for_page_to_load(*get_selector("WAIT_FOR_POST_TO_LOAD"))
        self.load_all_comments(*get_selector("LOAD_MORE_COMMENTS_BUTTON"))

        # some comments can be hidden when all comments are loaded
        self.view_hidden_comments()
        self.load_all_comment_replies(*get_selector("VIEW_MORE_REPLIES_BUTTON"))
        
        # get all comments through a container
        all_comments_container = self.driver.find_elements(*get_selector("ALL_COMMENTS_CONTAINER"))

        post_uuid = self.add_post_comment_to_DB(post_url, len(all_comments_container), account_name)

        # get comment detail per comment
        for r in all_comments_container:

            comment_container = r.find_element(*get_selector("COMMENT_CONTAINER"))
            comment_text = comment_container.find_element(*get_selector("COMMENT_TEXT")).text
            comment_owner = comment_container.find_element(*get_selector("COMMENT_OWNER")).text
            comment_likes = 0
            
            #comment likes can be None
            self.driver.implicitly_wait(0)
            comment_likes = self.find_element_with_possible_exception(comment_container, *get_selector("COMMENT_LIKES"))
            if comment_likes is not None:
                comment_likes = comment_likes.text
            self.driver.implicitly_wait(3)
            
            comment_date = comment_container.find_element(*get_selector("COMMENT_DATE")).get_attribute("datetime")

            # get replies to comment (can be None)
            replies_to_comment_container = []
            try:
                self.driver.implicitly_wait(0)
                replies_to_comment_container = r.find_elements(*get_selector("REPLIES_TO_COMMENT_CONTAINER"))
                self.driver.implicitly_wait(3)
            except TimeoutException: return
            except Exception as e: 
                print(e)

            # add comment to DB
            comment_entry = pd.Series({
                "post_url": post_url,
                "is_post": False,
                "commenter": comment_owner,
                "text": comment_text,
                "replies_to": None,
                "replies_count": len(replies_to_comment_container),
                "likes": comment_likes,
                "date": comment_date,
                "crawl_time": datetime.now()
            })
            comment_uuid = uuid.uuid4()
            self.DB.add_entry(comment_uuid, comment_entry)

            #add replies to comment to DB
            for reply in replies_to_comment_container:
                reply_text = reply.find_element(*get_selector("REPLY_TEXT")).text
                reply_owner = reply.find_element(*get_selector("REPLY_OWNER")).text
                reply_date = reply.find_element(*get_selector("REPLY_DATE")).get_attribute("datetime")
                reply_likes = 0
                self.driver.implicitly_wait(0)
                reply_likes = self.find_element_with_possible_exception(reply, *get_selector("REPLY_LIKES"))
                if reply_likes is not None:
                    reply_likes = reply_likes.text
                self.driver.implicitly_wait(3)

                #TODO: we dont know how many replies a single reply got
                #print("reply: ", reply_text, reply_owner, reply_likes)
                reply_entry = pd.Series({
                    "post_url": post_url,
                    "is_post": False,
                    "commenter": reply_owner,
                    "text": reply_text,
                    "replies_to": comment_uuid,
                    "replies_count": None,
                    "likes": reply_likes,
                    "date": reply_date,
                    "crawl_time": datetime.now()
                })
                self.DB.add_entry(uuid.uuid4(), reply_entry)

        self.DB.save_db_state()
        print("Done crawling post: ", post_url)
        return post_url

    def close_driver(self):
        """Closes driver.
        """
        self.driver.quit()
        self.driver.close()