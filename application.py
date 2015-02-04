import gio
import urllib
import appindicator
import pynotify
import gtk

import tweepy


CONSUMER_KEY = ''
CONSUMER_SECRET = ''

AUTH_TOKEN_KEY = ''
AUTH_TOKEN_SECRET = ''

def menuitem_response(w, buf):
    icon_url = ''
    # urllib.urlretrieve("http://some/remote/file.png", "/some/local/file.png")
    texto = '''<b>bold</b>
    and even <a href="http://google.com">links</a> are supported!'''
    pynotify.init('phytter')
    n = pynotify.Notification('Paulgramming Channel', texto)

    response = urllib.urlopen(icon_url)
    input_stream = gio.memory_input_stream_new_from_data(response.read())
    pixbuf = gtk.gdk.pixbuf_new_from_stream(input_stream)
    n.set_icon_from_pixbuf(pixbuf)
    n.show()


if __name__ == "__main__":
    ind = appindicator.Indicator("example-simple-client", "indicator-messages",
                                 appindicator.CATEGORY_APPLICATION_STATUS)
    ind.set_status(appindicator.STATUS_ACTIVE)
    ind.set_attention_icon("indicator-messages-new")

    # create a menu
    menu = gtk.Menu()

    # create some
    for i in range(3):
        buf = "Test-undermenu - %d" % i

        menu_items = gtk.MenuItem(buf)

        menu.append(menu_items)

        # this is where you would connect your menu item up with a function:

        menu_items.connect("activate", menuitem_response, buf)

        # show the items
        menu_items.show()

    ind.set_menu(menu)

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.secure = True
auth.set_access_token(AUTH_TOKEN_KEY, AUTH_TOKEN_SECRET)
# auth_url = auth.get_authorization_url()
# print('Please authorize: ' + auth_url)
# verifier = raw_input('PIN: ').strip()
# access_token = auth.get_access_token(verifier)
# print access_token

# api = API(auth)
api = tweepy.API(auth)

# print api.me().name
public_tweets = api.home_timeline()
# pynotify.init('tubecheck')
# for tweet in public_tweets:
    # n = pynotify.Notification("Notice", tweet.author.name, tweet.author.profile_image_url)
    # n.set_icon_from_pixbuf(gtk.Label().render_icon(gtk.STOCK_HARDDISK, gtk.ICON_SIZE_LARGE_TOOLBAR))
    # n.set_timeout(1000)
    # n.show()
    # print tweet.text
    # print tweet.author.name
    # print tweet.author.screen_name
    # print
    # print tweet.author.created_at

gtk.main()