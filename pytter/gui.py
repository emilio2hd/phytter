import gtk

import pytter


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