import unittest
import doctest

from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase.layer import onteardown
from Products.Five import fiveconfigure
from Zope2.App import zcml

import pmr2.app
from pmr2.testing.base import TestRequest
from pmr2.app.exposure.content import ExposureContainer
from pmr2.app.exposure.browser.browser import ExposureAddForm
from pmr2.app.exposure.browser.browser import ExposureFileGenForm
from pmr2.app.exposure.tests.base import ExposureDocTestCase
from pmr2.app.exposure.tests.base import ExposureExtendedDocTestCase


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


class CellMLDocTestCase(ExposureExtendedDocTestCase):

    def setUp(self):
        super(CellMLDocTestCase, self).setUp()
        import cellml.pmr2
        rev = u'2'
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

