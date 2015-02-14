import gtk

import pytter


def append_menu_about(menu, on_click_exit):
    image = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
    image.connect("activate", on_click_exit)
    image.show()
    menu.append(image)


def append_menu_quit(menu, on_click_exit):
    image = gtk.ImageMenuItem(gtk.STOCK_QUIT)
    image.connect("activate", on_click_exit)
    image.show()
    menu.append(image)


class AboutDialog(gtk.AboutDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        self.set_name(pytter.__name__)
        self.set_version(pytter.__version__)
        self.set_authors([pytter.__author__])
        self.set_comments(pytter.__comment__)
        self.set_website(pytter.__website__)
        self.set_logo(gtk.gdk.pixbuf_new_from_file("ico.png"))
        self.run()


class PinDialog(gtk.MessageDialog):
    def __init__(self):
        super(PinDialog, self).__init__(None, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK_CANCEL, "Enter PIN: ")

        self.set_title("Prompt")
        entry = gtk.Entry()
        self.vbox.add(entry)
        self.show_all()

        if self.run() == gtk.RESPONSE_CANCEL:
            self.pin = False
        else:
            self.pin = entry.get_text()

    def get_pin(self):
        return self.pin
