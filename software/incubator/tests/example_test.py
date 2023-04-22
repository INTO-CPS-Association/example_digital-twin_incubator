import unittest

from incubator.tests.cli_mode_test import CLIModeTest


class ExampleTestCase(CLIModeTest):

    def test_example_function(self):
        self.assertEqual(2, 2)
        if self.cli_mode():
            pass
            # This test is running from command line interface.
            # Avoid printing stuff, plotting, etc...
        else:
            # This test is running from an IDE, and plots therefore should be shown.
            print("Stuff")


if __name__ == '__main__':
    unittest.main()