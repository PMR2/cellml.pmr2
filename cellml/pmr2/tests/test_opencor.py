from os.path import dirname, join
import unittest

import zope.component

from pmr2.app.annotation.interfaces import IExposureNoteTarget
from pmr2.app.exposure.browser.browser import ExposureFileAnnotatorForm
from cellml.pmr2.annotator import OpenCORAnnotator

from pmr2.testing.base import TestRequest
from cellml.pmr2.tests.layer import CELLML_EXPOSURE_INTEGRATION_LAYER


class OpenCORTestCase(unittest.TestCase):

    layer = CELLML_EXPOSURE_INTEGRATION_LAYER

    def test_opencor_link(self):
        context = self.layer['portal'].unrestrictedTraverse(
            self.layer['exposure_file1_path'])
        request = TestRequest(
            form={
                'form.widgets.annotators': [u'opencor'],
                'form.buttons.apply': 1,
            })
        view = ExposureFileAnnotatorForm(context, request)
        view.update()  # should succeed.

        note = zope.component.queryAdapter(context, name='opencor')
        note.filename = 'README'

        urltool = zope.component.queryAdapter(
            context, IExposureNoteTarget, name='opencor')
        url = urltool('opencor')
        self.assertEqual(url,
            'opencor://openFile/http://nohost/plone/workspace/rdfmodel/rawfile'
            '/2/README')

        # Not really needed any longer, but kept here for completness.
        view = zope.component.queryMultiAdapter(
            (context, self.layer['portal'].REQUEST), name='opencor')
        view.__call__()
        self.assertEqual(
            view.request.response.headers,
            {'location':
                'http://nohost/plone/workspace/rdfmodel/@@rawfile/2/README'}
        )
