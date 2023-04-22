import os
import unittest


class CLIModeTest(unittest.TestCase):

    @staticmethod
    def cli_mode():
        """
        Check is the environment variable CLIMODE is defined.
        :return:
        """
        return "CLIMODE" in os.environ

    def ide_mode(self):
        return not self.cli_mode()
