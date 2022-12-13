OFFICIAL_ACCOUNT_NAME = 'elonmusk'
FAN_ACCOUNT_NAMES = ["elonmuskoffiicial", "elonmuskofflcial"]
BASE_URL = "https://www.instagram.com/"
TEST_ACCOUNT = "wdb_crawler"

COOKIE_POPUP = "XPATH,//*[text()='Allow essential and optional cookies']"
NOTIFICATION_POPUP = "XPATH,//*[text()='Not now']"
CURRENTLY_VISIBLE_POSTS = "CSS_SELECTOR,article a"
SEARCH_ICON = "CSS_SELECTOR,[aria-label=Search]"
SEARCH_INPUT = "CSS_SELECTOR,[aria-label='Search input']"
SEARCH_RESULT = "XPATH,//div[text()='{}']"
SEARCH_RESULTS = "CSS_SELECTOR,div[role='none'] div a"
WAIT_FOR_ACCOUNT_TO_LOAD = "XPATH,//h2[contains(text(),'{}')]"
WAIT_FOR_POST_TO_LOAD = "CSS_SELECTOR,li div>div div:nth-child(2)" #wait until comment container's presence located
HIDDEN_COMMENTS = "XPATH,.//*[contains(text(), 'View hidden')]"
POST_COMMENT = "CSS_SELECTOR,div[role='button'] li div div div:nth-child(2) div>span"
POST_LIKES = "CSS_SELECTOR,div[role='presentation'] div section:nth-child(2) div div div a div"
POST_DATE = "CSS_SELECTOR,div[role='presentation'] div div:nth-child(2) time"
LOAD_MORE_COMMENTS_BUTTON = "CSS_SELECTOR,[aria-label='Load more comments']"
VIEW_MORE_REPLIES_BUTTON = "XPATH,.//*[contains(text(), 'View replies') and @class='_a9yi']"
ALL_COMMENTS_CONTAINER = "CSS_SELECTOR,div[role='presentation'] ul>ul"
COMMENT_CONTAINER = "CSS_SELECTOR,li div>div div:nth-child(2)"
COMMENT_TEXT = "CSS_SELECTOR,div._a9zs span"
COMMENT_OWNER = "CSS_SELECTOR,h3"
COMMENT_LIKES = "XPATH,//div[contains(text(), 'like')]" #won't select text in comment itself, because the comment text is in a span
COMMENT_DATE = "CSS_SELECTOR,time"
REPLIES_TO_COMMENT_CONTAINER = "CSS_SELECTOR,li > ul > div[role='button']>li>div>div>div:nth-child(2)"
REPLY_TEXT = "CSS_SELECTOR,div._a9zs span"
REPLY_OWNER = "CSS_SELECTOR,h3"
REPLY_DATE = "CSS_SELECTOR,time"
REPLY_LIKES = "XPATH,//div[contains(text(), 'like')]" #won't select text in comment itself, because the comment text is in a span
PROFILE_SELECTOR = "XPATH,.//div[contains(text(), 'Profil')]"
USERNAME_INPUT = "NAME,username"
PASSWORD_INPUT = "NAME,password"
LOGIN_BUTTON = "CSS_SELECTOR,button[type='submit']"

## TEST
TEST_POST_COMMENT = "CSS_SELECTOR,div[role='button'] li div div div:nth-child(2) div>span"
TEST_POST_LIKES = "CSS_SELECTOR,div[role='presentation'] div section:nth-child(3) div div div a div"
TEST_POST_DATE = "CSS_SELECTOR,div[role='presentation'] div div:nth-child(2) time"