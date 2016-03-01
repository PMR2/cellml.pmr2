import zope.interface
import zope.schema

from pmr2.app.workspace.schema import StorageFileChoice


class ICellMLPMR2Layer(zope.interface.Interface):
    """CellML PMR2 Support layer"""


class ICmetaNote(zope.interface.Interface):
    """\
    CellML Metadata note.
    """

    metadata = zope.schema.Text(
        title=u'Metadata',
        description=u'The metadata content',
        required=False,
    )

    model_title = zope.schema.TextLine(
        title=u'Model Title',
        description=u'Title of the model',
        required=False,
    )

    model_author = zope.schema.TextLine(
        title=u'Model Author',
        description=u'Author of the model',
        required=False,
    )

    model_author_org = zope.schema.TextLine(
        title=u'Model Author Organization',
        description=u'Organization which the author is part of',
        required=False,
    )

    citation_authors = zope.schema.List(
        title=u'Citation Authors',
        description=u'List of authors of this citation',
        required=False,
    )

    citation_title = zope.schema.TextLine(
        title=u'Citation Title',
        description=u'The title of this citation (e.g. the title of a journal article)',
        required=False,
    )

    citation_bibliographicCitation = zope.schema.TextLine(
        title=u'Bibliographic Citation',
        description=u'The source of the article',
        required=False,
    )

    citation_id = zope.schema.TextLine(
        title=u'Citation Id',
        description=u'The unique identifier for this citation (such as Pubmed).',
        required=False,
    )

    citation_issued = zope.schema.TextLine(
        title=u'Citation Datetime',
        description=u'Taken from dcterms:issued.  Since the datetime format can be unpredictable, plain text is used.',
        required=False,
    )

    keywords = zope.schema.List(
        title=u'Keywords',
        description=u'The keywords of this model.',
        required=False,
    )


class IOpenCellSessionNote(zope.interface.Interface):
    """\
    OpenCell Session Note
    """

    filename = StorageFileChoice(
        title=u'Session File',
        description=u'The session file that is made for this file.  If not '
                     'selected, this file will be used for the "Launch" link.',
        vocabulary='pmr2.vocab.manifest',
        required=False,
    )


class IOpenCORNote(zope.interface.Interface):
    """
    OpenCOR Note
    """

    filename = StorageFileChoice(
        title=u'SedML file',
        description=u'The SedML file associated with this model file.  If not '
                     'selected, this file will be used for the "Launch" link.',
        vocabulary='pmr2.vocab.manifest',
        required=False,
    )


class ICellMLCodegenNote(zope.interface.Interface):
    """\
    Code generation results.
    """

    code = zope.schema.Dict(
        title=u'Code',
        description=u'Generated code.',
        default={},
        required=False,
    )


class ICellMLMathNote(zope.interface.Interface):
    """\
    Math notes
    """

    maths = zope.schema.List(
        title=u'Maths',
        description=u'Mathematic equations',
        default=[],
        required=False,
    )


class IPrefixMap(zope.interface.Interface):
    """
    A marker interface.
    """


class IVHostRemap(zope.interface.Interface):
    """
    For configuration registry for mapping a http(s?) url back to a
    pmr local url that our opener can use to access the raw model data
    directly.
    """

    prefix_maps = zope.schema.Dict(
        title=u'Virtual Host Prefix Mappings',
        description=u'Map a hostname to a valid physical path on this '
            'instance.  One per line, format is `hostname path`.',
        key_type=zope.schema.TextLine(
            title=u'Virtual Hostname',
        ),
        value_type=zope.schema.TextLine(
            # This could be a replacement if the vhost is actually done
            # on an alternative subpath.  Will implement when needed.
            title=u'Physical root',
        ),
    )

# XXX workaround the way IPersistentField adapts against things that
# alsoProvides something else but failing to properly persist the...
# persist interfaces even though the underlying object CLEARLY provides
# that...

from plone.registry.interfaces import IPersistentField
from persistent.interfaces import IPersistent

zope.interface.alsoProvides(IVHostRemap['prefix_maps'],
    IPrefixMap, IPersistentField, IPersistent)
