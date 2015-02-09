#!/usr/bin/env python

import gio
import os
import re
import urllib
import appindicator
import pynotify
import gtk
import logging
import sys
from threading import Thread
from textwrap import TextWrapper
from xml.etree.ElementTree import ElementTree, SubElement
from logging.handlers import SysLogHandler
from xml.sax.saxutils import escape

import tweepy
from dateutil.parser import parse
from dateutil.tz import tzlocal


gtk.gdk.threads_init()

LOG_FILENAME = '/var/log/pytter.log'
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

sh = SysLogHandler(address='/dev/log')
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)

logger = logging.getLogger("Pytter")
logger.setLevel(logging.ERROR)
logger.addHandler(sh)

VERSION = "0.1"
ABOUT_TXT = """A simple twitter watcher.

by: Emilio S. Carmo
<a href="mailto:emilio2hd@gmail.com">emilio2hd@gmail.com</a>
<a href="http://github.com/emilio2hd/pytter">http://github.com/emilio2hd/pytter</a>
"""

def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, *sys.argv)


class StreamWatcherListener(tweepy.StreamListener):
    status_wrapper = TextWrapper(width=60)

    def __init__(self, window):
        super(StreamWatcherListener, self).__init__()
        self.pytter = window

    def on_status(self, status):
        try:
            # print self.status_wrapper.fill(status.text)
            self.pytter.show_tweet(status)

            # print '\n %s  %s  via %s\n' % (status.author.screen_name, status.created_at, status.source)
        except:
            # Catch any unicode errors while printing to console
            # and just ignore them to avoid breaking application.
            pass

    def on_error(self, status_code):
        print(status_code)

    def on_timeout(self):
        print 'Snoozing Zzzzzz'


class StreamWatcherStarter(Thread):
    def __init__(self, auth, window):
        Thread.__init__(self)
        self.auth = auth
        self.window = window

    def run(self):
        stream = tweepy.Stream(auth=self.auth, listener=StreamWatcherListener(self.window))
        stream.userstream()


class Pytter():
    def __init__(self):
        self.stream = None
        self.root_dir = os.path.dirname(os.path.realpath(__file__))

        icon_image = self.root_dir + "/ico.png"
        if not os.path.isfile(icon_image):
            icon_image = "indicator-messages"

        self.ind = appindicator.Indicator("example-simple-client", icon_image, appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)

        self.menu = gtk.Menu()

        image = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        image.connect("activate", self.about)
        image.show()
        self.menu.append(image)

        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)

        image = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        image.connect("activate", self.sair)
        image.show()
        self.menu.append(image)

        self.menu.show()

        self.ind.set_menu(self.menu)

        self.settings = ElementTree()

        try:
            self.settings = ElementTree()
            self.settings.parse("settings.xml")
        except:
            logger.error("Fail to parse settings file.")
            sys.exit(1)

    def start(self):
        pynotify.init('phytter')

        if self.settings.find("oauth/accessToken") is None:
            gtk.idle_add(self.authenticate)
            return

        consumer_token = self.settings.find("oauth/consumerKey")
        consumer_secret = self.settings.find("oauth/consumerSecret")
        auth = tweepy.OAuthHandler(consumer_token.text, consumer_secret.text)

        access_token = self.settings.find("oauth/accessToken")
        access_token_secret = self.settings.find("oauth/accessTokenSecret")
        auth.set_access_token(access_token.text, access_token_secret.text)

        self.stream = StreamWatcherStarter(auth, self)
        self.stream.daemon = True
        self.stream.start()

    @staticmethod
    def gtk_prompt(name):
        prompt = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK_CANCEL, name)
        prompt.set_title("Prompt")
        # Create and add entry box to dialog
        entry = gtk.Entry()
        prompt.vbox.add(entry)
        # Show all widgets in prompt
        prompt.show_all()
        # Run dialog until user clicks OK or Cancel
        if prompt.run() == gtk.RESPONSE_CANCEL:
            # User cancelled dialog
            rval = False
        else:
            # User clicked OK, grab text from entry box
            rval = entry.get_text()
        # Destory prompt
        prompt.destroy()
        # Give the good (or bad) news
        return rval

    def authenticate(self):
        import webbrowser

        consumer_token = self.settings.find("oauth/consumerKey")
        consumer_secret = self.settings.find("oauth/consumerSecret")
        auth = tweepy.OAuthHandler(consumer_token.text, consumer_secret.text)

        redirect = ""
        try:
            redirect = auth.get_authorization_url()
        except tweepy.TweepError:
            logger.error("Failed to get request token.")

        webbrowser.open(redirect, 2, True)
        verifier = self.gtk_prompt("Enter PIN: ")

        try:
            auth.get_access_token(verifier)
            access_token = auth.get_access_token(verifier)
        except tweepy.TweepError:
            print "Error! Failed to get access token."

        api = tweepy.API(auth)
        if api.verify_credentials():
            xml_oauth = self.settings.find("oauth")
            xml_access_token = SubElement(xml_oauth, "accessToken")
            xml_access_token.text = auth.access_token
            xml_access_token_secret = SubElement(xml_oauth, "accessTokenSecret")
            xml_access_token_secret.text = auth.access_token_secret
            self.settings.write("settings.xml")
            restart_program()
        else:
            print "Error! OAuth credentials are incorrect."
        return False

    @staticmethod
    def show_tweet(tweet):
        # print tweet.author.created_at
        autor = "%s (@%s)" % (tweet.author.name, tweet.author.screen_name)
        timedate_str = parse(str(tweet.created_at) + " +0000").astimezone(tzlocal()).strftime("%x (%X)")

        # Use regexes to link URLs, hashtags, and usernames
        urlregex = re.compile("(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)",
                              re.IGNORECASE)

        texto = escape(tweet.text)
        texto = urlregex.sub(r'<a href="\1">\1</a>', texto)
        texto = re.sub(r'(\A|\s)@(\w+)', r'\1<a href="http://www.twitter.com/\2">@\2</a>', texto)
        texto = re.sub(r'(\A|\s)#(\w+)', r'\1<a href="C:HT#\2">#\2</a>', texto)
        texto += '''\n<small>%s</small>''' % timedate_str

        n = pynotify.Notification(autor, texto)

        response = urllib.urlopen(tweet.author.profile_image_url)
        input_stream = gio.memory_input_stream_new_from_data(response.read())
        pixbuf = gtk.gdk.pixbuf_new_from_stream(input_stream)
        n.set_icon_from_pixbuf(pixbuf)
        n.show()

    @staticmethod
    def sair(widget, data=None):
        gtk.main_quit()

    @staticmethod
    def about(widget, data=None):
        md = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE)
        try:
            md.set_markup("<b>Pytter %s</b>" % VERSION)
            md.format_secondary_markup(ABOUT_TXT)
            md.run()
        finally:
            md.destroy()

    def main(self):
        self.start()
        gtk.main()


if __name__ == '__main__':
    try:
        pytter = Pytter()
        pytter.main()
    except KeyboardInterrupt:
        print '\nGoodbye!'