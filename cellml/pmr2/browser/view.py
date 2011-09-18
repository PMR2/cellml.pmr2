import zope.component
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from paste.httpexceptions import HTTPNotFound
from plone.z3cform import layout

from pmr2.app.browser.layout import PlainTraverseLayoutWrapper
from pmr2.app.browser.layout import PlainLayoutWrapper

from pmr2.app.workspace.browser.browser import WorkspaceRawfileXmlBaseView
from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from pmr2.app.exposure.browser.browser import RawContentNote
from pmr2.app.exposure.browser.browser import ExposureFileViewBase

from pmr2.annotation.mathjax.layout import MathJaxLayoutWrapper
from pmr2.annotation.mathjax.layout import DeferredMathJaxLayoutWrapper
from pmr2.annotation.shjs.layout import IShjsLayoutWrapper
from pmr2.annotation.shjs.browser import SourceTextNote

from cellml.pmr2.util import fix_pcenv_externalurl


class ShjsTraverseLayoutWrapper(PlainTraverseLayoutWrapper):
    """
    A `PlainTraverseLayoutWrapper` that implements the Shjs wrapper.
    """

    zope.interface.implements(IShjsLayoutWrapper)

    def __call__(self):
        if hasattr(self.form_instance, 'update'):
            self.form_instance.update()
        if self.form_instance.rawcode:
            return self.form_instance.render()
        return super(ShjsTraverseLayoutWrapper, self).__call__()


class BasicMathMLNote(RawContentNote):
    """\
    This is based on the raw text note view, but uses the SourceTextNote
    browser class.
    """

    def template(self):
        # XXX yes this is a hack.
        return self.note.text.replace('<mml:', '<').replace('</mml:', '</')

BasicMathMLNoteView = layout.wrap_form(BasicMathMLNote,
    __wrapper_class=MathJaxLayoutWrapper)


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
    __wrapper_class=ShjsTraverseLayoutWrapper)


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
        keys = self.note.code.keys()
        keys.sort()
        return keys

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
        """\
        This must be called by the wrapper.  It does not do so by 
        default, so we wrap this around the customized layout wrapper
        defined above.
        """

        if not self.traverse_subpath:
            return 

        if len(self.traverse_subpath) > 2:
            raise HTTPNotFound()

        def select_language(language):
            if language not in self.available_langs():
                # we don't have this language.
                raise HTTPNotFound()
            self._language = language

        def check_raw(raw):
            if raw == 'raw':
                self.rawcode = True
            else:
                # unknown keyword.
                raise HTTPNotFound()

        process = [select_language, check_raw]

        for f, v in zip(process, self.traverse_subpath):
            f(v)

    def render(self):
        if self.language is None:
            return self.select_template()

        if self.rawcode:
            return self.raw()

        return super(CellMLCodegenNote, self).render()

CellMLCodegenNoteView = layout.wrap_form(CellMLCodegenNote, 
    __wrapper_class=ShjsTraverseLayoutWrapper)


class CmetaNote(ExposureFileViewBase):
    """\
    Cmeta note.
    """

    template = ViewPageTemplateFile('cmeta_note.pt')

CmetaNoteView = layout.wrap_form(CmetaNote, __wrapper_class=PlainLayoutWrapper)


class CellMLMathNote(ExposureFileViewBase):
    """\
    CellML Math Note.
    """

    template = ViewPageTemplateFile('cellml_math.pt')

    def maths(self):
        for comp, math in self.note.maths:
            yield {
                'id': comp,
                'math': ''.join(math),
            }

CellMLMathNoteView = layout.wrap_form(CellMLMathNote, 
    #__wrapper_class=PlainLayoutWrapper)
    #__wrapper_class=MathJaxLayoutWrapper)
    __wrapper_class=DeferredMathJaxLayoutWrapper)


class OpenCellSessionNoteView(ExposureFileViewBase):
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


class WorkspaceRawfileXmlBasePCEnvView(WorkspaceRawfileXmlBaseView):

    def find_type(self):
        # XXX we are not doing this for every single type, alternate
        # solution will be done.
        return 'application/x-pcenv-cellml+xml'

    def __call__(self):
        data = WorkspaceRawfileXmlBaseView.__call__(self)

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
