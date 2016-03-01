from rdflib.plugin import register
from rdflib.parser import Parser

from pmr2.app.annotation import note_factory as factory
from pmr2.app.annotation.note import RawTextNote

from note import *

BasicMathMLNoteFactory = factory(RawTextNote, 'basic_mathml')
BasicCCodeNoteFactory = factory(RawTextNote, 'basic_ccode')
CmetaNoteFactory = factory(CmetaNote, 'cmeta')
OpenCellSessionNoteFactory = factory(OpenCellSessionNote, 'opencellsession')
OpenCORNoteFactory = factory(OpenCORNote, 'opencor')
CellMLCodegenNoteFactory = factory(CellMLCodegenNote, 'cellml_codegen')
CellMLMathNoteFactory = factory(CellMLMathNote, 'cellml_math')

register(
    'cmeta', Parser,
    'cellml.pmr2.parser', 'RDFCmetaParser')
