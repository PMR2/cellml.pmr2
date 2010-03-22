from pmr2.app.factory import named_factory
from pmr2.app.annotation import note_factory
from pmr2.app.annotation.interfaces import *
from pmr2.app.annotation.annotator import ExposureFileAnnotatorBase

from cellml.pmr2.note import CellMLCodegenNote


class DummyCodegenAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'Dummy Code'
    description = u'A dummy code generator'
    
    def generate(self):
        return (
            ('code', {
                'C': 'printf("this is a test\\n");',
                'Python': 'print "this is a test"',
            }),
        )

DummyCodegenAnnotatorFactory = named_factory(DummyCodegenAnnotator)
DummyCodegenNoteFactory = note_factory(CellMLCodegenNote, 'dummy_code')
