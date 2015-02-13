import unittest

from pytter.utilities import Settings


class SettingsTestCase(unittest.TestCase):
    def test_has_token(self):
        settings = Settings("settings_empty.xml")
        self.assertFalse(settings.has_token())

    def test_consumer(self):
        settings = Settings()
        self.assertEquals("hjdjahushkaksu", settings.consumer_key())
        self.assertEquals("hfjhfakajshdlajsiuuisdfiusndjnfnxcskjdhsjkdhfuh", settings.consumer_secret())
        self.assertIsNone(settings.access_token())
        self.assertIsNone(settings.access_token_secret())


if __name__ == '__main__':
    unittest.main()
