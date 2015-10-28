import os
import sys
import re
from xml.etree.ElementTree import ElementTree, SubElement
from textwrap import TextWrapper
from xml.sax.saxutils import escape
from dateutil.parser import parse
from dateutil.tz import tzlocal
from threading import Thread

import tweepy

from pytter import logger


def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, *sys.argv)


class PytterUserStreamListener(tweepy.StreamListener):
    status_wrapper = TextWrapper(width=60)

    def __init__(self, application):
        super(PytterUserStreamListener, self).__init__()
        self.application = application

    def on_status(self, tweet):
        try:
            author = "%s (@%s)" % (tweet.author.name, tweet.author.screen_name)
            timedate_str = parse(str(tweet.created_at) + " +0000").astimezone(tzlocal()).strftime("%x (%X)")

            # Use regexes to link URLs, hashtags, and usernames
            urlregex = re.compile("(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)",
                                  re.IGNORECASE)

            text = escape(tweet.text)
            text = urlregex.sub(r'<a href="\1">\1</a>', text)
            text = re.sub(r'(\A|\s)@(\w+)', r'\1<a href="http://www.twitter.com/\2">@\2</a>', text)
            text = re.sub(r'(\A|\s)#(\w+)', r'\1<a href="C:HT#\2">#\2</a>', text)
            text += '''\n<small>%s</small>''' % timedate_str

            self.application.show_tweet(text, author, tweet.author.profile_image_url)
        except:
            print("Unicode error.")
            # Catch any unicode errors while printing to console
            # and just ignore them to avoid breaking application.
            pass

    def on_error(self, status_code):
        logger.error(status_code)


class PytterUserStream(Thread):
    def __init__(self, auth, application):
        Thread.__init__(self)
        self.auth = auth
        self.application = application

    def run(self):
        stream = tweepy.Stream(auth=self.auth, listener=PytterUserStreamListener(self.application))
        stream.userstream()


class Settings:
    SETTINGS_FILENAME = "settings.xml"
    OAUTH_CONSUMER_KEY_PATH = "oauth/consumerKey"
    OAUTH_CONSUMER_SECRET_PATH = "oauth/consumerSecret"
    OAUTH_ACCESS_TOKEN_PATH = "oauth/accessToken"
    OAUTH_ACCESS_TOKEN_SECRET_PATH = "oauth/accessTokenSecret"

    def __init__(self, filename=SETTINGS_FILENAME):
        self.settings = ElementTree()
        self.settings.parse(filename)

    def consumer_secret(self):
        consumer_secret = self.settings.find(self.OAUTH_CONSUMER_SECRET_PATH)
        if consumer_secret is not None:
            return consumer_secret.text

        return None

    def consumer_key(self):
        consumer_key = self.settings.find(self.OAUTH_CONSUMER_KEY_PATH)
        if consumer_key is not None:
            return consumer_key.text

        return None

    def access_token(self):
        access_token = self.settings.find(self.OAUTH_ACCESS_TOKEN_PATH)
        if access_token is not None:
            return access_token.text

        return None

    def access_token_secret(self):
        access_token_secret = self.settings.find(self.OAUTH_ACCESS_TOKEN_SECRET_PATH)
        if access_token_secret is not None:
            return access_token_secret.text

        return None

    def has_token(self):
        return self.access_token() is not None

    def write_access(self, access_token, access_token_secret):
        xml_oauth = self.settings.find("oauth")
        xml_access_token = SubElement(xml_oauth, "accessToken")
        xml_access_token.text = access_token
        xml_access_token_secret = SubElement(xml_oauth, "accessTokenSecret")
        xml_access_token_secret.text = access_token_secret
        self.settings.write(self.SETTINGS_FILENAME)
