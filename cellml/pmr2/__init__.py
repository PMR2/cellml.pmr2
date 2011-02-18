from pmr2.app.annotation import note_factory as factory
from pmr2.app.annotation.note import RawTextNote

from note import *

BasicMathMLNoteFactory = factory(RawTextNote, 'basic_mathml')
BasicCCodeNoteFactory = factory(RawTextNote, 'basic_ccode')
CmetaNoteFactory = factory(CmetaNote, 'cmeta')
OpenCellSessionNoteFactory = factory(OpenCellSessionNote, 'opencellsession')
CellMLCodegenNoteFactory = factory(CellMLCodegenNote, 'cellml_codegen')
CellMLMathNoteFactory = factory(CellMLMathNote, 'cellml_math')
