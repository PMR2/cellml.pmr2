import zope.component
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from paste.httpexceptions import HTTPNotFound
from plone.z3cform import layout

from pmr2.app.interfaces import IExposureSourceAdapter
from pmr2.app.browser.exposure import RawContentNote, ExposureFileViewBase
from pmr2.app.browser.layout import PlainTraverseOverridableWrapper
from pmr2.app.browser.layout import PlainLayoutWrapper


class BasicCCodeNote(RawContentNote):
    """\
    This is a raw content view, where the raw text is rendered as a
    struture as per the default template.
    """

    template = ViewPageTemplateFile('basic_ccode.pt')
    description = u'The following is a raw representation of the file.'
    subtitle = u'Raw content view'

    def content(self):
        return self.note.text

    def raw(self):
        self.request.response.setHeader('Content-Type', 'text/plain')
        return self.note.text

    def __call__(self):
        if not self.traverse_subpath:
            return super(BasicCCodeNote, self).__call__()
        elif self.traverse_subpath[0] == 'raw':
            return self.raw()
        else:
            raise HTTPNotFound()

BasicCCodeNoteView = layout.wrap_form(BasicCCodeNote,
    __wrapper_class=PlainTraverseOverridableWrapper)


class CmetaNote(ExposureFileViewBase):
    """\
    Wraps an object around the mathml view.
    """

    template = ViewPageTemplateFile('cmeta_note.pt')

CmetaNoteView = layout.wrap_form(CmetaNote, __wrapper_class=PlainLayoutWrapper)


class OpenCellSessionNoteView(ExposureFileViewBase):
    # XXX change this when we have better/generalized
    target_view = 'pcenv'

    def __call__(self):
        if self.note.filename is None:
            # no session specified.
            raise HTTPNotFound()
        helper = zope.component.queryAdapter(
            self.context, IExposureSourceAdapter)
        exposure, workspace, path = helper.source()
        target_uri = '%s/@@%s/%s/%s' % (workspace.absolute_url(), 
            self.target_view, exposure.commit_id, self.note.filename)
        return self.request.response.redirect(target_uri)
