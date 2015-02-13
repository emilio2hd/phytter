import os
import sys
from xml.etree.ElementTree import ElementTree, SubElement


def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, *sys.argv)


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