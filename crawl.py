import argparse
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import sys
sys.path.insert(0, '../')
from utils.database import InstagramDatabase

import os
from dotenv import load_dotenv
load_dotenv()

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from utils.instagram_crawler import InstagramCrawler

def print_checkpoint_messages(path, last_post_crawled, current_post):
    """Prints useful comments to retry crawling of posts.

    Args:
        path (_type_): _description_
        last_post_crawled (_type_): _description_
        current_post (): _description_
    """
    print("********************************")
    print(f"Use the arguments: \n'-posts {path} -from-post-url {last_post_crawled}'\nto retry crawling starting from the same post.")
    print("********************************")
    print(f"Use the arguments: \n'-posts {path} -from-post-url {current_post}'\nto retry and skip the current post.")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-account-name', required=True, help="Required. The account name of the account to be crawled.")
    parser.add_argument('-posts', required=False, help="Default: None. If set to a valid path to a parseable file of post urls, then crawler will skip getting all post urls step and use the urls in the file instead.")
    parser.add_argument('-only-get-post-urls', default=False, type=bool, help="Default: False. If set to True, script ends after storing all post urls.")
    parser.add_argument('-from-post-url', help="Default: None. If set to a valid post-url, the crawler will begin crawling posts from the index of the given post url in the parseable file of post urls. ATTENTION: Instaram Posts will be stored in the following format: 'https://www.instagram.com/p/[post id]/'")
    args = parser.parse_args()
    DB = InstagramDatabase('./data/tabular/' + args.account_name + '.csv')
    driver = webdriver.ChromiumEdge(service=Service(EdgeChromiumDriverManager().install()))
    crawler = InstagramCrawler(driver, DB)
    
    # if -posts argument is None, we can generate a new post url list file
    if args.posts is None:
        posts = crawler.get_all_posts(args.account_name)
        
        # open file in write mode
        path = './data/' + args.account_name + '-post-urls.txt'
        with open(path, 'w+') as fp:
            for post_url in posts:
                # write each item on a new line
                fp.write("%s\n" % posts[post_url])
        print(f'Done saving {len(posts)} post url(s) to file.')

    # if -only_get_post_urls is True, we can exit the script 
    if args.only_get_post_urls and args.posts is None:
        print("Exiting...")
        exit()
    
    # if -only_get_post_urls is True and the user has specified a list of post urls, the script won't do anything
    if args.only_get_post_urls and args.posts is not None:
        print("Try setting either -only-get-post-urls to False or delete the -posts argument. Exiting...")
        exit()

    # if -posts is not None, we can use the specified list of post urls
    if args.posts is not None:
        posts = []

        path = args.posts
        # check if path exists, if not, then abort
        if os.path.exists(path) is not True:
            print("Path to existing post url list doesn't exist. Exiting...")
            exit()

        # open file and read the content in a list
        with open(path, 'r') as fp:
            try:
                for line in fp:
                    x = line[:-1]
                    posts.append(x)
            except Exception as e:
                print("Exception while trying to parse post url file: ", e)
                print("Exiting...")
                exit()

    # define the start index inside the post url list
    start_index = 0
    if type(posts) == dict:
        posts = list(posts.values())

    # start index is defined by -from_post_url argument
    if args.from_post_url != None:
        try:
            start_index = posts.index(args.from_post_url) + 1
        except Exception as e:
            print(f"Exception while trying to identify which post to start crawling process. Tried finding {args.from_post_url}: ", e)
            exit()

    # log the last post crawled
    last_post_crawled = None
    iterator = range(start_index, len(posts))
    if len(iterator) == 0:
        print("No posts found to crawl. Exiting...")
        exit()

    #if args.posts is not None it won't have crawled the posts before, therefore we need to login.
    crawler.refresh_crawler(logged_in=(args.posts is None))
    for i in iterator:
        try:
            last_post_crawled = crawler.crawl_post(posts[i], args.account_name)
        except Exception as e:
            print(f"Error trying to crawl post with url {posts[i]}: ", e)
            print_checkpoint_messages(path, last_post_crawled, posts[i])
            exit()
        except KeyboardInterrupt:
            print("Keyboard interrupt detected.")
            print_checkpoint_messages(path, last_post_crawled, posts[i])
            exit()

    print(f"Done Crawling {len(iterator)} posts. Exiting...")