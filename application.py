#!/usr/bin/env python

import gio
import os
import urllib
import appindicator
import pynotify
import gtk
import sys

import tweepy

from pytter.gui import AboutDialog, PinDialog, append_menu_about, append_menu_quit
from pytter.utilities import restart_program, Settings, PytterUserStream
from pytter import logger


gtk.gdk.threads_init()


class Application():
    def __init__(self):
        self.stream = None
        self.root_dir = os.path.dirname(os.path.realpath(__file__))

        icon_image = self.root_dir + "/ico.png"
        if not os.path.isfile(icon_image):
            icon_image = "indicator-messages"

        self.indicator = appindicator.Indicator("pytter", icon_image, appindicator.CATEGORY_APPLICATION_STATUS)
        self.indicator.set_status(appindicator.STATUS_ACTIVE)

        self.menu = gtk.Menu()

        append_menu_about(self.menu, self.on_click_about)

        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)

        append_menu_quit(self.menu, self.on_click_quit)

        self.menu.show()
        self.indicator.set_menu(self.menu)

        try:
            self.settings = Settings()
        except:
            logger.error("Fail to parse settings file.")
            sys.exit(1)

    def start(self):
        pynotify.init('phytter')

        if not self.settings.has_token():
            gtk.idle_add(self.authenticate)
            return

        auth = tweepy.OAuthHandler(self.settings.consumer_key(), self.settings.consumer_secret())
        auth.set_access_token(self.settings.access_token(), self.settings.access_token_secret())

        self.stream = PytterUserStream(auth, self)
        self.stream.daemon = True
        self.stream.start()

    def authenticate(self):
        import webbrowser

        auth = tweepy.OAuthHandler(self.settings.consumer_key(), self.settings.consumer_secret())

        redirect = ""
        try:
            redirect = auth.get_authorization_url()
        except tweepy.TweepError:
            logger.error("Failed to get request token.")

        webbrowser.open(redirect, 2, True)
        pin = self.get_pin_from_prompt()

        try:
            auth.get_access_token(pin)
        except tweepy.TweepError:
            logger.error("Error! Failed to get access token.")
            sys.exit(1)

        api = tweepy.API(auth)
        if api.verify_credentials():
            self.settings.write_access(auth.access_token, auth.access_token_secret)
            restart_program()
        else:
            logger.error("Error! OAuth credentials are incorrect.")

        return False

    @staticmethod
    def show_tweet(text, author, author_profile_image_url):
        notification = pynotify.Notification(author, text)

        response = urllib.urlopen(author_profile_image_url)
        input_stream = gio.memory_input_stream_new_from_data(response.read())
        pixbuf = gtk.gdk.pixbuf_new_from_stream(input_stream)

        notification.set_icon_from_pixbuf(pixbuf)
        notification.show()

    @staticmethod
    def on_click_quit(widget, data=None):
        gtk.main_quit()

    @staticmethod
    def on_click_about(widget, data=None):
        AboutDialog().destroy()

    @staticmethod
    def get_pin_from_prompt():
        prompt = PinDialog()
        pin = prompt.get_pin()
        prompt.destroy()

        return pin

    def main(self):
        self.start()
        gtk.main()


if __name__ == '__main__':
    try:
        Application().main()
    except KeyboardInterrupt:
        print '\nGoodbye!'