import unittest

from plone.app.testing import logout
from zExceptions import Unauthorized

from cellml.pmr2.urlopener import PmrUrlOpener
from cellml.pmr2.tests.layer import CELLML_EXPOSURE_INTEGRATION_LAYER
from cellml.pmr2.tests.layer import CELLML_EXPOSURE_INTEGRATION_LIVE_LAYER

# a single instance _should_ suffice
opener = PmrUrlOpener()


class UrlOpenerLocalTestCase(unittest.TestCase):

    layer = CELLML_EXPOSURE_INTEGRATION_LAYER

    def test_safe_standard_load_standard(self):
        f = opener.loadURL('pmr:/plone/workspace/test:2:dir1/f2')
        self.assertEqual(f, 'second file in dir1\n')

    def test_safe_standard_load_unauthorized(self):
        logout()
        self.assertRaises(Unauthorized, opener.loadURL,
            'pmr:/plone/workspace/test:2:dir1/f2')

    def test_safe_standard_load_anonymous(self):
        logout()
        f = opener.loadURL('pmr:/plone/workspace/main_bucket:0:README')
        self.assertEqual(f, 'A test main repo.\n')


class UrlOpenerSpawnedTestCase(unittest.TestCase):

    layer = CELLML_EXPOSURE_INTEGRATION_LIVE_LAYER

    def test_safe_standard_load(self):
        f = opener.loadURL('pmr:/plone/workspace/test:2:dir1/f2')
        self.assertEqual(f, 'second file in dir1\n')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UrlOpenerLocalTestCase))
    suite.addTest(unittest.makeSuite(UrlOpenerSpawnedTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()

