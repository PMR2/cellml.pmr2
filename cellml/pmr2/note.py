import zope.interface
import zope.component
from zope.schema import fieldproperty

from pmr2.processor.cmeta import Cmeta
from pmr2.app.interfaces import *
from pmr2.app.annotation.note import RawTextNote
from pmr2.app.annotation.note import ExposureFileNoteBase
from pmr2.app.annotation.note import ExposureFileEditableNoteBase

from interfaces import *
from util import uri2http, normal_kw

# CellML Specific notes storage classes.


class CmetaNote(ExposureFileNoteBase):
    """\
    Contains a rendering of the CellML Metadata.
    """
    # XXX this class should be part of the metadata, and registered into
    # some sort of database that will automatically load this up into
    # one of the valid document types that can be added.

    zope.interface.implements(ICmetaNote)

    metadata = fieldproperty.FieldProperty(ICmetaNote['metadata'])

    model_title = fieldproperty.FieldProperty(ICmetaNote['model_title'])
    model_author = fieldproperty.FieldProperty(ICmetaNote['model_author'])
    model_author_org = fieldproperty.FieldProperty(ICmetaNote['model_author_org'])

    citation_authors = fieldproperty.FieldProperty(ICmetaNote['citation_authors'])
    citation_title = fieldproperty.FieldProperty(ICmetaNote['citation_title'])
    citation_bibliographicCitation = fieldproperty.FieldProperty(ICmetaNote['citation_bibliographicCitation'])
    citation_id = fieldproperty.FieldProperty(ICmetaNote['citation_id'])
    citation_issued = fieldproperty.FieldProperty(ICmetaNote['citation_issued'])
    keywords = fieldproperty.FieldProperty(ICmetaNote['keywords'])

    def citation_authors_string(self):
        if not self.citation_authors:
            return u''
        middle = u'</li>\n<li>'.join(
            ['%s, %s %s' % i for i in self.citation_authors])
        return u'<ul>\n<li>%s</li>\n</ul>' % middle

    def citation_id_html(self):
        if not self.citation_id:
            return u''
        http = uri2http(self.citation_id)
        if http:
            return '<a href="%s">%s</a>' % (http, self.citation_id)
        return self.citation_id

    def get_authors_family_index(self):
        if self.citation_authors:
            return [normal_kw(i[0]) 
                    for i in self.citation_authors]
        else:
            return []

    def get_citation_title_index(self):
        if self.citation_title:
            return normal_kw(self.citation_title)

    def get_keywords_index(self):
        if self.keywords:
            results = [normal_kw(i[1]) for i in self.keywords]
            results.sort()
            return results
        else:
            return []

    def keywords_string(self):
        return ', '.join(self.get_keywords_index())

    def pmr1_citation_authors(self):
        if self.citation_authors and self.citation_issued:
            authors = u', '.join([i[0] for i in self.citation_authors])
            return u'%s, %s' % (authors, self.citation_issued[:4])
        else:
            return u''

    def pmr1_citation_title(self):
        if self.citation_title:
            return self.citation_title
        else:
            return u''


class OpenCellSessionNote(ExposureFileEditableNoteBase):
    """\
    Points to the OpenCell session attached to this file.
    """

    zope.interface.implements(IOpenCellSessionNote)
    filename = fieldproperty.FieldProperty(IOpenCellSessionNote['filename'])
