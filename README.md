# Web Crawler, WDB Module Mini-Challenge 2

![example workflow](https://github.com/github/docs/actions/workflows/main.yaml/badge.svg)

# Motivation

Automated extraction of data from social platforms like Instagram enables us to gain invaluable insight into social  trends, accounts engagement value, or current (social and political) trends. This information is not relevant only for research, but also for marketing and product design purposes, because it enables the stakeholders to understand their clients or audience better. 

We wanted to practice our scraping skills on Instagram and we chose an account dedicated to Elon Musk. He has been galvanizing the public opinion with his controversial business decisions and we were interested in the content that such an account would have. We expected the comments to be less structured than Twitter replies.

Instagram has dynamic elements on its site, so to fully crawl an account we used Selenium instead of other libraries that use simple requests. Another reason for choosing Selenium is its ability to circumvent the log-in windows that Instagram has. Some of the content on Instagram is even hidden for signed-out users. The code will also be extendable to crawl other accounts. Especially political accounts could be appealing.

We crawl through the Elon Musk's account maintained by his fans: https://www.instagram.com/elonmusk/

## Data Structure

  For each post we crawl through every comment and its replies. The data is stored in a .csv file with the parameters:

| Column name   | Type | Description                                                                                       |
|---------------|------|---------------------------------------------------------------------------------------------------|
| post_id       | str  | URL to post                                                                                       |
| is_post       | bool | post (TRUE) or comment (FALSE)                                                                    |
| text          | str  | post/comment content                                                                              |
| replies_to    | str  | uuid; empty if original post, id of the post if comment                                           |
| replies_count | int  | number of replies per post                                                                        |
| likes         | int  | number of likes per post                                                                          |
| date          | str  | date of post: comments will be in weeks from the time of crawl; example: 2022-12-01T01:40:25.000Z |
| crawl_time    | str  | date of crawling; example: 2022-12-02 01:43:22.864370                                             |                                                                                     |

# Getting started

To crawl the data, you need to specify an Instagram username and password. Please contact bruno.baptistakreiner@students.fhnw.ch or katarina.fatur@students.fhnw.ch for the test account details.

## Running in docker

Running the crawler requires you to provide:

- absolute_path_to_folder: Absolute path to where you want the crawled to store data on your PC. Example: **/tmp**
- output_file: File name of the csv file. Example: **data.csv**
- username: Username of the Instagram account.
- password: Password of the Instagram account.

To run the crawler in docker, execute in your terminal, from the root of this project:

```bash
# Substitute the parameters absolute_path_to_folder, username, password with appropriate values.
docker run \ 
  -v <absolute_path_to_folder>:/data \ 
  --env DB_CONNECTION_STRING=/data/<output_file>.csv \
  --env INSTAGRAM_USERNAME=<username> \
  --env INSTAGRAM_PASSWORD=<password> \
  wdb-scraper
```

An example command might be:
```bash
# Example command
docker run \
  -v /tmp:/data \
  --env DB_CONNECTION_STRING=/data/elonmusk.csv \
  --env INSTAGRAM_USERNAME=ScraperUser \
  --env INSTAGRAM_PASSWORD=SecretPassword \
  wdb-scraper
```

## Building docker container

To build an image tagged **wdb-scraper** run from the root of this project:

```bash
sh build_docker.sh
```

## Manual setup

To crawl the data on your machine, you need to specify an Instagram Account inside an .env file. 
An example is given inside ./.env-example. Rename that file to .env and add the password for the crawler to work.

 - INSTAGRAM_USERNAME = ""
 - INSTAGRAM_PASSWORD = ""

To create and activate the environment with the name [environment_name] you can use: 

```bash
python -m venv [environment_name]
source ./[environment_name]/Scripts/activate (leave out "source" on windows)
````

To then install all dependencies inside the environment, use:
```bash
pip install -r requirements.txt
```
To run the crawler, use:

```bash
python crawl.py -account-name [account name to be crawled]
```
To see the accepted arguments, type:

```bash
python crawl.py -h
```

For each crawl the crawler goes through the same steps: Crawling all post URLs, storing those URLs in a text file inside the ./data/ folder and then iterating through each URL to get the post data and store it in the database inside ./data/tabular/. For each post, the crawler first loads all the comments then loads all the potential replies to each comment and finally stores all the information in the database. 

!Attention!: The crawler will name the files with all the post URLs like the following: 
 - [account-name]-post-urls.txt for the list of post URLs of an account
 - [account-name].csv for all the comments found on the account's posts
If a crawler crawls the same account twice, it will simply add new rows to the csv. This will result in duplicated that will need to be checked later.

The crawl script accepts the following arguments:
 - **account-name**: Required. The account name of the account to be crawled.
 - **posts**: Defaults to None. If set to a valid txt file with one post URL per line, the crawler will skip getting all posts of an account and try to crawl through each line in the file.
 - **only-get-post-urls**: Defaults to False. If set to True, script ends after storing all post URLs and won't crawl through the posts itself.
 - **from-post-url**: Defaults to None. If set to a valid post URL in the format 'https://www.instagram.com/p/[post id]/', the crawler will find the index of the post URL in the posts file and begin crawling posts from the index of the given post URL.

## Project dependencies

### Scraper
The following libraries need to be installed on the machine to run the scraper:

- selenium==4.7.2
- webdriver_manager==3.8.5
- matplotlib
- missingno==0.5.1
- pandas
- python-dotenv

All requirements are added to the requirements.txt file.

### Data analysis
The following libraries need to be installed on the machine to run the data_analysis.ipynb:

- pandas
- emoji
- plotly
- nltk
- wordcloud

These requirements are _not_ added to the requirements.txt file because they are not meant to be run with regularly.

## Running the tests

To run the test and check if the selectors are still working, use:

```bash
python -m unittest tests.py
```

This will test all selectors on the "wdb_crawler" account on Instagram. To test all selectors, the most recent comment on the most recent post of the account has to have likes and more than one reply with the most recent reply also having a like so that selectors for likes and replies can be tested. If tests fail, there might be a potential network error, you've been blocked by Instagram or the most recent posts has new comments (they can be manually deleted). 

The selectors are tested on whether they throw a NoSuchElementException or not. If they do, a accurate error message is shown and the test fails. Due to Selenium driver issues, the main test function couldn't be refactored into smaller functions.

# Project architecture

The project stores data in the data folder. Crawled post data is stored in the ./data/tabular folder in a CSV file. The crawler stores all post URLs in a text file directly into the ./data folder itself. The filenames of the post URLs and the crawled posts are the same for every crawl.

# Selenium Selectors

Some elements on Instagram have specific texts that are rather selected using XPATH's powerful contains() and text() functions. These elements are the cookie popup, the notification popup, the hidden comments button, the "View more replies"-button and the comment and reply likes-button (the text is hidden but that doesn't matter). Furthermore, to check whether the account page has loaded we check whether there is an "h2" element with the account name in it. CSS is used for all the other selectors except for the username and password input elements because they can be selected using the name attribute. CSS is easy to read and faster than XPATH. Selecting comments is done using a hierarchical approach where first the container of all comments is selected, then for each comment, all the info is retrieved. Selecting first the container then the items can also be used to retrieve replies to a comment. This way we don't need to select all replies and figure out which comment is their parent through CSS' ":has" selector or XPATH queries that are hard to understand. A lot of the elements on Instagram have useless class names that don't indicate what the element stands for. There are some elements though where the "type" or "aria-label" attribute has been set to something useful.

# Additional Information

- The option to hide offensive comments was turned off in the profile settings of the crawler account.

- We tried to find a way to inform Instagram about the crawler account for research purposes, but we couldn't find the contact information.

# Known Issues

- ## Account block
 - Instagram has a ton of checks to see whether you're automating data crawling. Instagram might block your account's requests or prevent you from logging in for a couple of minutes to hours, but won't ban you immediately. They will also first try to make you register for a 2FA (two factor authentication). During testing, no account was permanently blocked. Multiple short sleeps were implemented to slow down Selenium.
 - We did not have time to extensively test the limits of the sleeps. They were set to a reasonable 3 seconds for loading more account posts, 3 seconds for loading more comments under a post and 1 second for loading replies to a comment. There is also a 10 second timeout for waiting to be logged in and for a post to load.

- ## Request Timeouts
 - Sometimes Instagram blocks your requests without making it clear on the webpage. Loading more posts/comments/replies to comments might take forever, or it sends you the same data again and again as a way to not combat a lot of requests to their servers. Catching all of these problems is not easy. We implement tests in ./tests.py to first check whether the selectors are working and add some conditions inside the code that check whether new data is being retrieved.

- ## Other Problems
 - Crawling your own account in which you're logged into will make Selenium miss the post _likes_ attribute for crawling a post. This is because Instagram adds some stats for you to see on your own posts. This issue will be fixed in the future by changing the selector to find the likes by selecting an element that contains the text "like(s)". 
 You can bypass this issue by setting the POST_LIKES selector in config.py to search for section:nth-child(3) instead of section:nth-child(2).
 - If post is video, it will show views instead of likes.
 - If a post has over 1000+ comments, it will probably crash the application, or take you a loooong time to crawl all the comments.
 - https://www.instagram.com/p/CbYN9LKIjHb/?next=%2F, https://www.instagram.com/p/CODS5yPBVHq/?next=%2F, https://www.instagram.com/p/CODJ9fJBwmQ/?next=%2F and https://www.instagram.com/p/CN2vzH3h3zv/?next=%2F crashed the page (probably too many comments).
 - Unnamed 0.0 - 0.6 were generated probably because the columns for the unique identifier was not specified and unnamed columns were generated. These need to be concatenated when preprocessing the data for data analysis.
 - Some information can be None and won't throw an error if the crawler doesn't find the element. For those elements, we can test whether the selector works by creating specific tests for them in Unittests.

- ## General Selenium Stuff
 - Selenium implicitly waits for 10 seconds for an element even if WebDriverWait().until() is used with a 1 second wait. This default setting can be overwritten using WebDriver.implicitly_wait(0) before WebDriverWait().until().  

- ## Fixed Issues 
 - If a comment has "View replies" in its text it will make the application go on forever. Fixed by adding a class element to the selector.

- ## TODOS:
 - Check the amount of comments in a post before and after clicking on "load more comments" to test whether Instagram has blocked off the crawler or if there are internet problems. This is already being tested in tests.py but need to be brought to the crawler itself. Same needs to be implemented/tested for loading replies to comments and loading more posts.
 - Check why UUIDs are not stored correctly as one single column.