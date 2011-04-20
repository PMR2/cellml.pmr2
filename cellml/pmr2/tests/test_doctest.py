import unittest

from zope.testing import doctestunit, doctest
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase.layer import onteardown
from Products.Five import fiveconfigure
from Zope2.App import zcml

import pmr2.app
from pmr2.app.tests.base import TestRequest
from pmr2.app.exposure.content import ExposureContainer
from pmr2.app.exposure.browser.browser import ExposureAddForm
from pmr2.app.exposure.browser.browser import ExposureFileGenForm
from pmr2.app.exposure.tests.base import ExposureDocTestCase

from pmr2.mercurial.tests.base import MercurialDocTestCase

@onsetup
def setup():
    import pmr2.app
    import cellml.pmr2
    fiveconfigure.debug_mode = True
    # XXX dependant on pmr2.app still
    zcml.load_config('configure.zcml', cellml.pmr2)
    zcml.load_config('test.zcml', cellml.pmr2.tests)
    fiveconfigure.debug_mode = False
    ztc.installPackage('cellml.pmr2')

@onteardown
def teardown():
    pass

setup()
teardown()
ptc.setupPloneSite(products=('cellml.pmr2',))


class CellMLDocTestCase(MercurialDocTestCase):

    def setUp(self):
        super(CellMLDocTestCase, self).setUp()
        import cellml.pmr2
        self.portal['exposure'] = ExposureContainer()
        rawrevs = [
            'b94d1701154be42acf63ee6b4bd4a99d09ba043c',
            '2647d4389da6345c26d168bbb831f6512322d4f9',
            '006f11cd9211abd2a879df0f6c7f27b9844a8ff2',
        ]
        rawrev = rawrevs[2]
        rev = unicode(rawrev)
        request = TestRequest(
            form={
                'form.widgets.workspace': u'rdfmodel',
                'form.widgets.commit_id': rev,
                'form.buttons.add': 1,
            })
        testform = ExposureAddForm(self.portal.exposure, request)
        testform.update()
        exp_id = testform._data['id']
        context = self.portal.exposure[exp_id]
        self.exposure1 = context
        rdfmodel = self.portal.workspace.rdfmodel
        self.file1 = u'example_model.cellml'
        request = TestRequest(
            form={
                'form.widgets.filename': [self.file1],
                'form.buttons.add': 1,
            })
        testform = ExposureFileGenForm(context, request)
        testform.update()
        self.exposure_file1 = context[self.file1]


def test_suite():
    return unittest.TestSuite([

        # General tests.
        ztc.ZopeDocFileSuite(
            'cellml.txt', package='cellml.pmr2',
            test_class=CellMLDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # Cataloging tests.
        ztc.ZopeDocFileSuite(
            'catalog.txt', package='cellml.pmr2',
            test_class=CellMLDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # Code viewer tests
        ztc.ZopeDocFileSuite(
            'browser/code.txt', package='cellml.pmr2',
            test_class=CellMLDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        doctestunit.DocTestSuite(
            module='cellml.pmr2.util',
            setUp=testing.setUp, tearDown=testing.tearDown
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
