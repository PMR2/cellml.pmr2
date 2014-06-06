from os.path import dirname, join
import unittest

import zope.component
from plone.testing import z2

from pmr2.app.exposure.browser.browser import ExposureFileAnnotatorForm

from pmr2.testing.base import TestRequest

from cellml.pmr2.tests.layer import CELLML_EXPOSURE_INTEGRATION_LAYER


class CodegenTestCase(unittest.TestCase):

    layer = CELLML_EXPOSURE_INTEGRATION_LAYER

    def test_base_codegen(self):
        context = self.layer['portal'].unrestrictedTraverse(
            self.layer['exposure_file1_path'])
        request = TestRequest(
            form={
                'form.widgets.annotators': [u'cellml_codegen'],
                'form.buttons.apply': 1,
            })
        view = ExposureFileAnnotatorForm(context, request)
        view.update()
        note = zope.component.getAdapter(context, name='cellml_codegen')
        langkeys = note.code.keys()
        self.assertIn('C', langkeys)
        self.assertIn('F77', langkeys)
        self.assertIn('MATLAB', langkeys)
        self.assertIn('Python', langkeys)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodegenTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()

