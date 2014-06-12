import unittest
from urllib2 import URLError

import zope.component
from plone.app.testing import logout
from plone.registry.interfaces import IRegistry
from zExceptions import Unauthorized

from pmr2.app.workspace.exceptions import PathNotFoundError
from pmr2.app.workspace.exceptions import RevisionNotFoundError
from cellml.api.pmr2.interfaces import UnapprovedProtocolError
from cellml.api.pmr2.interfaces import ICellMLAPIUtility

from cellml.pmr2.urlopener import PmrUrlOpener
from cellml.pmr2.tests.layer import CELLML_EXPOSURE_INTEGRATION_LAYER
from cellml.pmr2.tests.layer import CELLML_EXPOSURE_INTEGRATION_LIVE_LAYER

# a single instance _should_ suffice
opener = PmrUrlOpener()


class UrlOpenerUtilityTestCase(unittest.TestCase):

    def test_urljoin_standard(self):
        # standard support code path.
        r = opener.urljoin('http://www.example.com/testmodel.cellml',
            'newmodel/a.cellml')
        self.assertEqual(r, 'http://www.example.com/newmodel/a.cellml')

    def test_urljoin_nonstandard(self):
        r = opener.urljoin('pmr:/some/path:1:/file',
            'newmodel/a.cellml')
        self.assertEqual(r, 'pmr:/some/path:1:/newmodel/a.cellml')
    
    def test_urljoin_nonstandard_multi(self):
        r = opener.urljoin('pmr:/some/path:1:/another/path/file',
            '../to/a.cellml')
        self.assertEqual(r, 'pmr:/some/path:1:/another/to/a.cellml')



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


class CellMLLoaderTestCase(unittest.TestCase):

    layer = CELLML_EXPOSURE_INTEGRATION_LAYER

    def test_model_load_standard(self):
        cu = zope.component.getUtility(ICellMLAPIUtility)
        target = 'pmr:/plone/workspace/main_model:0:/model.cellml'
        model = cu.loadModel(target, loader=opener)
        self.assertEqual(sorted([i.name for i in model.modelComponents]),
            ['bucket', 'tap'])
        maths = cu.extractMaths(model)
        self.assertEqual(sorted(dict(maths).keys()), ['bucket', 'tap'])

    def test_model_load_relative_import_local(self):
        cu = zope.component.getUtility(ICellMLAPIUtility)
        target = 'pmr:/plone/workspace/main_model:0:/demo.cellml'
        model = cu.loadModel(target, loader=opener)
        self.assertEqual(sorted([i.name for i in model.modelComponents]),
            ['bucket1', 'environment', 'tap1'])
        maths = cu.extractMaths(model)
        self.assertEqual(sorted(dict(maths).keys()),
            ['bucket', 'environment', 'tap'])

    def test_model_load_embedded_undefined_vhost_map(self):
        cu = zope.component.getUtility(ICellMLAPIUtility)
        target = 'pmr:/plone/workspace/demo_model:0:/multi.cellml'
        model = cu.loadModel(target, loader=opener)
        # model loaded but imports cannot be instantiated.
        self.assertEqual([i.wasInstantiated for i in model.imports],
            [False, False, False])

    def test_model_load_embedded_defined_vhost_map(self):
        registry = zope.component.getUtility(IRegistry)
        registry['cellml.pmr2.vhost.prefix_maps'] = {u'nohost': u''}
        cu = zope.component.getUtility(ICellMLAPIUtility)
        target = 'pmr:/plone/workspace/demo_model:0:/multi.cellml'
        model = cu.loadModel(target, loader=opener)
        self.assertEqual(sorted([i.name for i in model.modelComponents]),
            ['bucket1', 'bucket2', 'bucket3', 'environment', 'tap1'])
        maths = cu.extractMaths(model)
        self.assertEqual(sorted(dict(maths).keys()),
            ['bucket', 'environment', 'tap'])

    def test_model_load_embedded_defined_vhost_map_pathed(self):
        registry = zope.component.getUtility(IRegistry)
        registry['cellml.pmr2.vhost.prefix_maps'] = {u'nohost': u'/plone'}
        cu = zope.component.getUtility(ICellMLAPIUtility)
        target = 'pmr:/plone/workspace/demo_modelt:0:/multi.cellml'
        model = cu.loadModel(target, loader=opener)
        self.assertEqual(sorted([i.name for i in model.modelComponents]),
            ['bucket1', 'bucket2', 'bucket3', 'environment', 'tap1'])
        maths = cu.extractMaths(model)
        self.assertEqual(sorted(dict(maths).keys()),
            ['bucket', 'environment', 'tap'])

    def test_model_load_embedded_defined_vhost_map_privateblock(self):
        registry = zope.component.getUtility(IRegistry)
        registry['cellml.pmr2.vhost.prefix_maps'] = {u'nohost': u''}
        logout()
        cu = zope.component.getUtility(ICellMLAPIUtility)
        target = 'pmr:/plone/workspace/demo_modelp:0:/multi.cellml'
        self.assertRaises(Unauthorized, cu.loadModel, target, loader=opener)


class CellMLLoaderLiveTestCase(unittest.TestCase):

    layer = CELLML_EXPOSURE_INTEGRATION_LIVE_LAYER

    def test_model_load_embedded_undefined_vhost_map(self):
        cu = zope.component.getUtility(ICellMLAPIUtility)
        target = 'pmr:/plone/workspace/demo_live:0:/multi.cellml'
        model = cu.loadModel(target, loader=opener)
        # model loaded, imports loaded via http
        self.assertEqual(sorted([i.name for i in model.modelComponents]),
            ['bucket1', 'bucket2', 'bucket3', 'environment', 'tap1'])
        maths = cu.extractMaths(model)
        self.assertEqual(sorted(dict(maths).keys()),
            ['bucket', 'environment', 'tap'])

    def test_model_load_embedded_defined_vhost_map(self):
        registry = zope.component.getUtility(IRegistry)
        registry['cellml.pmr2.vhost.prefix_maps'] = {u'localhost:55001': u''}
        cu = zope.component.getUtility(ICellMLAPIUtility)
        target = 'pmr:/plone/workspace/demo_live:0:/multi.cellml'
        model = cu.loadModel(target, loader=opener)
        self.assertEqual(sorted([i.name for i in model.modelComponents]),
            ['bucket1', 'bucket2', 'bucket3', 'environment', 'tap1'])
        maths = cu.extractMaths(model)
        self.assertEqual(sorted(dict(maths).keys()),
            ['bucket', 'environment', 'tap'])

    def test_model_load_embedded_undefined_vhost_map_privateblock(self):
        # no need to log out because credentials over http are not passed.
        cu = zope.component.getUtility(ICellMLAPIUtility)
        target = 'pmr:/plone/workspace/demo_livep:0:/multi.cellml'
        # Native CellML failed, permission.
        self.assertRaises(ValueError, cu.loadModel, target, loader=opener)

    def test_model_load_embedded_defined_vhost_map_internal(self):
        registry = zope.component.getUtility(IRegistry)
        registry['cellml.pmr2.vhost.prefix_maps'] = {u'localhost:55001': u''}
        # no need to log out because credentials over http are not passed.
        cu = zope.component.getUtility(ICellMLAPIUtility)
        target = 'pmr:/plone/workspace/demo_livep:0:/multi.cellml'
        # successfully loaded because vhost is defined, and accessible
        # through internal methods.
        model = cu.loadModel(target, loader=opener)
        self.assertEqual(sorted([i.name for i in model.modelComponents]),
            ['bucket1', 'bucket2', 'bucket3', 'environment', 'tap1'])
        maths = cu.extractMaths(model)
        self.assertEqual(sorted(dict(maths).keys()),
            ['bucket', 'environment', 'tap'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UrlOpenerLocalTestCase))
    suite.addTest(unittest.makeSuite(UrlOpenerSpawnedTestCase))
    suite.addTest(unittest.makeSuite(CellMLLoaderTestCase))
    suite.addTest(unittest.makeSuite(CellMLLoaderLiveTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()

