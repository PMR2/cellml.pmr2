import zope.component
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from paste.httpexceptions import HTTPNotFound
from plone.z3cform import layout

from pmr2.app.interfaces import IExposureSourceAdapter
from pmr2.app.browser.exposure import RawContentNote, ExposureFileViewBase
from pmr2.app.browser.workspace import WorkspaceRawfileXmlBaseView
from pmr2.app.browser.layout import PlainTraverseOverridableWrapper
from pmr2.app.browser.layout import PlainLayoutWrapper

from pmr2.annotation.shjs.layout import IShjsLayoutWrapper
from pmr2.annotation.shjs.browser import SourceTextNote

from cellml.pmr2.util import fix_pcenv_externalurl


class ShjsPlainTraverseOverridableWrapper(PlainTraverseOverridableWrapper):
    """
    A `PlainTraverseOverridableWrapper` that implements the Shjs 
    wrapper.
    """

    zope.interface.implements(IShjsLayoutWrapper)


class BasicCCodeNote(SourceTextNote):
    """\
    This is based on the raw text note view, but uses the SourceTextNote
    browser class.
    """

    # used by template
    title = ViewPageTemplateFile('basic_ccode.pt')
    langtype = u'cpp'

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
    __wrapper_class=ShjsPlainTraverseOverridableWrapper)


class CellMLCodegenNote(SourceTextNote):
    """\
    CellML Code Generation note.
    """

    template = ViewPageTemplateFile('cellml_code.pt')

    def __call__(self):
        return self.template()

CellMLCodegenNoteView = layout.wrap_form(CellMLCodegenNote, 
    __wrapper_class=ShjsPlainTraverseOverridableWrapper)

class CmetaNote(ExposureFileViewBase):
    """\
    Cmeta note.
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


class WorkspaceRawfileXmlBasePCEnvView(WorkspaceRawfileXmlBaseView):

    def find_type(self):
        # XXX we are not doing this for every single type, alternate
        # solution will be done.
        return 'application/x-pcenv-cellml+xml'

    def __call__(self):
        data = WorkspaceRawfileXmlBaseView.__call__(self)

        if self.storage.path.endswith('session.xml'):
            # See pmr2.app.util.fix_pcenv_externalurl and
            # https://tracker.physiomeproject.org/show_bug.cgi?id=1079
            data = fix_pcenv_externalurl(data, self.rooturi)

        contentType = self.find_type()
        # since content type has been changed, and data may have been
        # regenerated
        self.request.response.setHeader('Content-Type', contentType)
        self.request.response.setHeader('Content-Length', len(data))

        return data