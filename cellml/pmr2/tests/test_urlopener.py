import unittest
from urllib2 import URLError

import zope.component
from plone.app.testing import logout
from plone.registry.interfaces import IRegistry
from zExceptions import Unauthorized

from pmr2.app.workspace.exceptions import PathNotFoundError
from pmr2.app.workspace.exceptions import RevisionNotFoundError
from cellml.api.pmr2.interfaces import UnapprovedProtocolError

from cellml.pmr2.urlopener import PmrUrlOpener
from cellml.pmr2.tests.layer import CELLML_EXPOSURE_INTEGRATION_LAYER
from cellml.pmr2.tests.layer import CELLML_EXPOSURE_INTEGRATION_LIVE_LAYER

# a single instance _should_ suffice
opener = PmrUrlOpener()


class UrlOpenerLocalTestCase(unittest.TestCase):

    layer = CELLML_EXPOSURE_INTEGRATION_LAYER

    # test standard way, ala the default codegen test.
    # test various failure modes
    # - wrong encoding of uri
    # fallback modes, i.e. fallback to http:// with mercurial
    # relative uri access to embedded workspaces with mercurial 

    def test_safe_standard_load_missing_obj(self):
        self.assertRaises(AttributeError, opener.loadURL,
            'pmr:/plone/workspace/missing:4:/dir1/f2')

    def test_safe_standard_load_missing_file(self):
        self.assertRaises(PathNotFoundError, opener.loadURL,
            'pmr:/plone/workspace/test:2:/dir1/not_file')

    def test_safe_standard_load_missing_rev(self):
        self.assertRaises(RevisionNotFoundError, opener.loadURL,
            'pmr:/plone/workspace/test:24:/dir1/not_file')

    def test_safe_standard_load_wrong_obj(self):
        self.assertRaises(TypeError, opener.loadURL,
            'pmr:/plone/workspace:0:/dir1/not_file')

    def test_safe_standard_load_malformed_uri(self):
        self.assertRaises(ValueError, opener.loadURL,
            'pmr:/plone/workspace')

    def test_safe_standard_load_standard(self):
        f = opener.loadURL('pmr:/plone/workspace/test:2:/dir1/f2')
        self.assertEqual(f, 'second file in dir1\n')

    def test_safe_standard_load_unauthorized(self):
        logout()
        self.assertRaises(Unauthorized, opener.loadURL,
            'pmr:/plone/workspace/test:2:/dir1/f2')

    def test_safe_standard_load_bad_protocol(self):
        self.assertRaises(UnapprovedProtocolError, opener,
            'ftp://localhost/workspace/test/2/dir1/f2')

    def test_safe_standard_load_anonymous(self):
        logout()
        f = opener.loadURL('pmr:/plone/workspace/main_model:0:/README')
        self.assertEqual(f, 'A test main repo.\n')

    def test_embedded_load_unregistered_vhost(self):
        # Will result in loading from http://nohost/, which will fail
        # under normal circumstances.
        self.assertRaises(URLError, opener.loadURL,
            'pmr:/plone/workspace/external_root:0:/external_test/test.txt')

    def test_embedded_load_registered_vhost(self):
        registry = zope.component.getUtility(IRegistry)
        registry['cellml.pmr2.vhost.prefix_maps'] = {u'nohost': u''}
        f = opener.loadURL(
            'pmr:/plone/workspace/external_root:0:/external_test/test.txt')
        self.assertEqual(f, 'external test file.\n')

    def test_embedded_load_registered_http(self):
        registry = zope.component.getUtility(IRegistry)
        registry['cellml.pmr2.vhost.prefix_maps'] = {u'nohost': u''}

        # While it would be nice if dumb absolute links are used,
        # generally this will result in a local model that will fail to
        # work anyway, so we won't do this.
        # f = opener.loadURL(

        # Instead we will treat this as a failure.
        self.assertRaises(URLError, opener.loadURL,
            'http://nohost/plone/workspace/external_root/'
            'rawfile/0/external_test/test.txt')
        #self.assertEqual(f, 'external test file.\n')


class UrlOpenerSpawnedTestCase(UrlOpenerLocalTestCase):

    # Repeat the test above, with the live integration layer.
    layer = CELLML_EXPOSURE_INTEGRATION_LIVE_LAYER

    def test_safe_standard_load_http(self):
        f = opener.loadURL('http://localhost:55001/plone/workspace/'
            'main_model/@@rawfile/0/README')
        self.assertEqual(f, 'A test main repo.\n')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UrlOpenerLocalTestCase))
    suite.addTest(unittest.makeSuite(UrlOpenerSpawnedTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()

