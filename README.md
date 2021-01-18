# wallscrape
reddit image scraper in python

dependencies:
```
python -m pip install Pillow praw
```

modify the json with your own client ID and secret hash.

To generate your own CID and secret, follow [this](https://www.reddit.com/prefs/apps) link. Click **create another app**, click the **script** bubble, and put `http://localhost:8080` in the **redirect URI** block. Fill out the name and description with whatever, then click **create app**. The secret hash should be displayed as a labelled field within the app's section. The client ID is underneath "personal use script".
