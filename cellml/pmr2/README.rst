-----------------------
CellML PMR2 Annotations
-----------------------

In PMR2 v0.1, the Cmeta views was implemented as a separate type, now
it is reimplemented as an annotator and has been split out from PMR2
Application Core.

Here we first set up the environment.
::

    >>> from pprint import pprint
    >>> from zope import interface
    >>> import zope.component
    >>> from plone.z3cform.tests import setup_defaults
    >>> from pmr2.app.exposure.browser.browser import ExposureFileAnnotatorForm
    >>> from pmr2.app.exposure.browser.browser import ExposureFileNoteEditForm
    >>> from pmr2.testing.base import TestRequest
    >>> pp = lambda x: pprint(x, indent=4, width=1)

First we make the note using the form, then we view the output using
the view registered.
::

    >>> filectx = self.exposure_file1
    >>> request = TestRequest(
    ...     form={
    ...         'form.widgets.annotators': [u'cmeta'],
    ...         'form.buttons.apply': 1,
    ...     })
    >>> view = ExposureFileAnnotatorForm(filectx, request)
    >>> result = view()
    >>> result == ''
    True

That should have generated all the data needed for the cmeta view.
::

    >>> request = TestRequest()
    >>> view = zope.component.queryMultiAdapter(
    ...     (filectx, request), name='cmeta')
    >>> view = view.form_instance
    >>> print view()
    <h1>Model Metadata</h1>
    <h3>CellML Model Authorship</h3>
    <dl>
    <dt>Title:</dt>
    <dd></dd>
    <dt>Author:</dt>
    <dd>Given Family</dd>
    <dt>Organisation:</dt>
    <dd>Example Subsidary, Example Organization</dd>
    </dl>
    <h3>Citation</h3>
    <dl>
    <dt>Authors:</dt>
    <dd><ul>
    <li>Family1, Given1 ...</li>
    <li>Family2, G </li>
    <li>Family2, H W</li>
    </ul></dd>
    <dt>Title:</dt>
    <dd>One Example Paper</dd>
    <dt>Source:</dt>
    <dd>Journal of Example Subject</dd>
    <dt>Identifier:</dt>
    <dd><a href="http://www.ncbi.nlm.nih.gov/pubmed/1111111111">urn:miriam:pubmed:1111111111</a></dd>
    <dt>Model Keywords:</dt>
    <dd>cardiac, electrophysiology, ventricular_myocyte</dd>
    </dl>

Session files are kind of different, since currently there isn't a way
to determine one as they are not linked (not strictly true, it can be
determined by parsing all session files, but it is currently not within
the scope to do so).  So we allow the user to specify one and attached
to the file as a note.  However, some notes are not meant for users to
edit for some content are not compatible with sanitization after the
generation was done, so we have the editable note implement a marker
interface of some sort.  Anyway, we test out editing first on the
session file note/annotator.
::

    >>> filectx = self.exposure_file1
    >>> request = TestRequest(
    ...     form={
    ...         'form.widgets.annotators': [u'opencellsession'],
    ...         'form.buttons.apply': 1,
    ...     })
    >>> view = ExposureFileAnnotatorForm(filectx, request)
    >>> result = view()
    >>> result == ''
    True
    >>> request.response.getHeader('Location')
    'http://.../example_model.cellml/@@note_editor/opencellsession'

We should have been a redirect to the edit view.  The editor view is
defined without any default fields, so it must figure out the correct
fields from the name of the note from the URI supplied.  We replicate
what the request would see here and render the note edit view.
::

    >>> session_path = u'component/docs/index.html'
    >>> request = TestRequest()
    >>> view = ExposureFileNoteEditForm(filectx, request)
    >>> view.traverse_subpath = ['opencellsession']
    >>> result = view()
    >>> 'filename' in result
    True
    >>> session_path in result
    True

We first apply a default none value, which should update.
::

    >>> request = TestRequest(
    ...     form={
    ...         'form.widgets.filename': [],
    ...         'form.buttons.apply': 1,
    ...     })
    >>> view = ExposureFileNoteEditForm(filectx, request)
    >>> view.traverse_subpath = ['opencellsession']
    >>> result = view()

Now if we call the OpenCell session note view for the file, it will
redirect to the CellML file.
::

    >>> request = TestRequest()
    >>> view = zope.component.queryMultiAdapter((filectx, request), 
    ...                                         name='opencellsession')
    >>> result = view()
    >>> print request.response.getHeader('Location')
    http://...rdfmodel/@@pcenv/.../example_model.cellml

Now we apply the session path to the note.
::

    >>> request = TestRequest(
    ...     form={
    ...         'form.widgets.filename': [session_path],
    ...         'form.buttons.apply': 1,
    ...     })
    >>> view = ExposureFileNoteEditForm(filectx, request)
    >>> view.traverse_subpath = ['opencellsession']
    >>> result = view()

It will now redirect to the session file.
::

    >>> request = TestRequest()
    >>> view = zope.component.queryMultiAdapter((filectx, request), 
    ...                                         name='opencellsession')
    >>> result = view()
    >>> print request.response.getHeader('Location')
    http://...rdfmodel/@@pcenv/.../component/docs/index.html
