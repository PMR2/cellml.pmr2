from cStringIO import StringIO
import zope.component

from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from cellml.pmr2.cmeta import Cmeta
from pmr2.annotation.citation.utility import CitationFormatterBase


class CellMLCitationFormatter(CitationFormatterBase):
    """\
    Extracts dcterms:license from CellML file.
    """

    title = u'CellML RDF Metadata'

    def extract(self):
        helper = zope.component.queryAdapter(
            self.context, IExposureSourceAdapter)
        input = helper.file()
        metadata = Cmeta(StringIO(input))
        license = metadata.get_license()
        return license
