import zope.component
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.interfaces import NotFound

from pmr2.app.workspace.browser.browser import WorkspaceRawfileXmlBase
from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from pmr2.app.exposure.browser.browser import ExposureFileViewBase

from pmr2.annotation.mathjax.browser import DeferredMathJaxNote
from pmr2.annotation.shjs.browser import SourceTextNote

from cellml.pmr2.util import fix_pcenv_externalurl

try:
    from pmr2.bives.view import call_bives
    BIVES = True
except ImportError:
    BIVES = False


class BasicCCodeNote(SourceTextNote):
    """\
    This is based on the raw text note view, but uses the SourceTextNote
    browser class.
    """

    # used by template
    label = ViewPageTemplateFile('basic_ccode.pt')
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
            raise NotFound(self.context, self.traverse_subpath[0])


class CellMLCodegenNote(SourceTextNote):
    """\
    CellML Code Generation note.
    """

    select_template = ViewPageTemplateFile('code_select.pt')
    title = ViewPageTemplateFile('cellml_code.pt')
    rawcode = False

    def raw(self):
        self.request.response.setHeader('Content-Type', 'text/plain')
        return self.content()

    def content(self):
        return self.note.code[self.language]

    def available_langs(self):
        return sorted(self.note.code.keys())

    @property
    def langtype(self):
        # this is to be compatible with shjs.
        if self.language:
            return self.language.lower()

    @property
    def language(self):
        if hasattr(self, '_language'):
            return self._language

    def update(self):

        if not self.traverse_subpath:
            return

        if len(self.traverse_subpath) > 2:
            raise NotFound(self.context, self.traverse_subpath[-1])

        def select_language(language):
            if language not in self.available_langs():
                # we don't have this language.
                raise NotFound(self.context, language)
            self._language = language

        def check_raw(raw):
            if raw == 'raw':
                self.rawcode = True
            else:
                # unknown keyword.
                raise NotFound(self.context, raw)

        process = [select_language, check_raw]

        for f, v in zip(process, self.traverse_subpath):
            f(v)

    def render(self):
        if self.rawcode:
            return self.raw()

        if self.language is None:
            self.template = self.select_template

        return super(CellMLCodegenNote, self).render()


class CmetaNote(ExposureFileViewBase):
    """\
    Cmeta note.
    """

    template = ViewPageTemplateFile('cmeta_note.pt')
    label = 'Model Metadata'


class CellMLMathNote(DeferredMathJaxNote):
    """\
    CellML Math Note.
    """

    template = ViewPageTemplateFile('cellml_math.pt')

    def has_bives(self):
        return BIVES

    def maths(self):
        for comp, math in self.note.maths:
            yield {
                'id': comp,
                'math': ''.join(math),
            }


class CellMLBiVeSMathView(CellMLMathNote):

    template = ViewPageTemplateFile('cellml_bives_math.pt')

    @property
    def note(self):
        # This is currently leveraging the standard view as above.
        return zope.component.queryAdapter(self.context, name='cellml_math')

    def update(self):
        super(CellMLBiVeSMathView, self).update()
        self.bives_results = '{"error": "pmr2.bives is not installed."}'
        if not BIVES:
            return
        self.bives_results = call_bives([self.context.absolute_url()],
            ['singleCompHierarchyJson',])


class OpenCellSessionNote(ExposureFileViewBase):
    # XXX change this when we have better/generalized
    target_view = 'pcenv'

    def __call__(self):
        helper = zope.component.queryAdapter(
            self.context, IExposureSourceAdapter)
        exposure, workspace, path = helper.source()
        filename = self.note.filename or path
        target_uri = '%s/@@%s/%s/%s' % (workspace.absolute_url(),
            self.target_view, exposure.commit_id, filename)
        return self.request.response.redirect(target_uri)


class WorkspaceRawfileXmlBasePCEnv(WorkspaceRawfileXmlBase):

    def find_type(self):
        # XXX we are not doing this for every single type, alternate
        # solution will be done.
        return 'application/x-pcenv-cellml+xml'

    def __call__(self):
        data = WorkspaceRawfileXmlBase.__call__(self)

        if self.viewpath.endswith('session.xml'):
            # See pmr2.app.util.fix_pcenv_externalurl and
            # https://tracker.physiomeproject.org/show_bug.cgi?id=1079
            data = fix_pcenv_externalurl(data, self.rooturi)

        contentType = self.find_type()
        # since content type has been changed, and data may have been
        # regenerated
        self.request.response.setHeader('Content-Type', contentType)
        self.request.response.setHeader('Content-Length', len(data))

        return data
