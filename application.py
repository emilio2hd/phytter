#!/usr/bin/env python

import gio
import os
import re
import urllib
import appindicator
import pynotify
import gtk
import sys
from threading import Thread
from textwrap import TextWrapper
from xml.etree.ElementTree import ElementTree, SubElement
from xml.sax.saxutils import escape

import tweepy
from dateutil.parser import parse
from dateutil.tz import tzlocal

from pytter.gui import AboutDialog
from pytter.utilities import restart_program
from pytter import logger


gtk.gdk.threads_init()


class StreamWatcherListener(tweepy.StreamListener):
    status_wrapper = TextWrapper(width=60)

    def __init__(self, window):
        super(StreamWatcherListener, self).__init__()
        self.pytter = window

    def on_status(self, status):
        try:
            self.pytter.show_tweet(status)
        except:
            # Catch any unicode errors while printing to console
            # and just ignore them to avoid breaking application.
            pass

    def on_error(self, status_code):
        logger.error(status_code)


class StreamWatcherStarter(Thread):
    def __init__(self, auth, window):
        Thread.__init__(self)
        self.auth = auth
        self.window = window

    def run(self):
        stream = tweepy.Stream(auth=self.auth, listener=StreamWatcherListener(self.window))
        stream.userstream()


class Application():
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

        entry = gtk.Entry()
        prompt.vbox.add(entry)

        prompt.show_all()

        if prompt.run() == gtk.RESPONSE_CANCEL:
            rval = False
        else:

            rval = entry.get_text()

        prompt.destroy()

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
        except tweepy.TweepError:
            logger.error("Error! Failed to get access token.")

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
            logger.error("Error! OAuth credentials are incorrect.")
        return False

    @staticmethod
    def show_tweet(tweet):

        autor = "%s (@%s)" % (tweet.author.name, tweet.author.screen_name)
        timedate_str = parse(str(tweet.created_at) + " +0000").astimezone(tzlocal()).strftime("%x (%X)")

        # Use regexes to link URLs, hashtags, and usernames
        urlregex = re.compile("(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)",
                              re.IGNORECASE)

        text = escape(tweet.text)
        text = urlregex.sub(r'<a href="\1">\1</a>', text)
        text = re.sub(r'(\A|\s)@(\w+)', r'\1<a href="http://www.twitter.com/\2">@\2</a>', text)
        text = re.sub(r'(\A|\s)#(\w+)', r'\1<a href="C:HT#\2">#\2</a>', text)
        text += '''\n<small>%s</small>''' % timedate_str

        n = pynotify.Notification(autor, text)

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
        AboutDialog().destroy()

    def main(self):
        self.start()
        gtk.main()


if __name__ == '__main__':
    try:
        Application().main()
    except KeyboardInterrupt:
        print '\nGoodbye!'