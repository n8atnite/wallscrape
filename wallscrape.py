# wallpaper scraping tool for reddit
# searches common image subreddits and grabs images based on @params
# removes images older than one month (intended to be run as a cronjob)

# @params
# resolution -> 4K minimum, 16:9 enforced
# upvotes -> TODO
# color (average RGB value within specified range) -> TODO

import os
import praw
import time
import urllib
import json
from PIL import Image
import signal

# load reddit api data from file
api_data = json.load(open('api.json',))
APP_CLIENTID = api_data['clientID']
APP_SECRET = api_data['secret']
APP_USERAGENT = api_data['userAgent']
APP_SUBS = api_data['subs']
FILETYPES = ['.jpg', '.jpeg', '.png']
PATH = os.path.abspath('/opt/wallscrape/')
if not os.path.exists(PATH):
    os.mkdir(PATH)
ASPECT_RATIO = round(16/9, 3)

class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

# grab posts from subs, top 10 in hot
# dict holds posts, key -> imgID, value -> dict of image metadata
post_data = {} # key -> post id; value -> url, title, score, timestamp
reddit = praw.Reddit(client_id = APP_CLIENTID,
                     client_secret = APP_SECRET,
                     user_agent = APP_USERAGENT)
subs = [reddit.subreddit(sr) for sr in APP_SUBS]
for sub in subs:
    posts = sub.hot(limit=10)
    for post in posts:
        post_data[post.id] = {
            'url': post.url,
            'title': post.title,
        }

# download to local
for imageID, data in post_data.items():
    url = data['url']
    ext = os.path.splitext(url)[1]
    if ext in FILETYPES:
        try:
            image_path = os.path.join(PATH, imageID + ext)
            print('>>> downloading ', data['title'], ' at ', url)
            with timeout(seconds=10):
                urllib.request.urlretrieve(url, image_path)
        except:
            print('>>>>>> ERROR: could not download image at ', url)
            continue
    
        # remove images with incorrect aspect ratio
        try:
            image = Image.open(image_path)
        except FileNotFoundError:
            print(">>>>>> ERROR: file ", image_path, " not found. Skipping...")
            continue
        image_ratio = round(image.size[0]/image.size[1], 3)
        if (image_ratio != ASPECT_RATIO) or (image.size[0] < 3840) or (image.size[1] < 2160):
            image.close()
            os.remove(image_path)
        else:
            image.close()

# cleanup old files (30 days)
for file in os.listdir(PATH):
    fpath = os.path.join(PATH, file)
    if os.path.getmtime(fpath) < (time.time()-2592000):
        print(">>> cleaning old file...")
        os.remove(fpath)
