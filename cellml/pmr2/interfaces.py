import zope.interface
import zope.schema


class ICmetaNote(zope.interface.Interface):
    """\
    CellML Metadata note.
    """

    metadata = zope.schema.Text(
        title=u'Metadata',
        description=u'The metadata content',
    )

    model_title = zope.schema.TextLine(
        title=u'Model Title',
        description=u'Title of the model',
    )

    model_author = zope.schema.TextLine(
        title=u'Model Author',
        description=u'Author of the model',
    )

    model_author_org = zope.schema.TextLine(
        title=u'Model Author Organization',
        description=u'Organization which the author is part of',
    )

    citation_authors = zope.schema.List(
        title=u'Citation Authors',
        description=u'List of authors of this citation',
    )

    citation_title = zope.schema.TextLine(
        title=u'Citation Title',
        description=u'The title of this citation (e.g. the title of a journal article)',
    )

    citation_bibliographicCitation = zope.schema.TextLine(
        title=u'Bibliographic Citation',
        description=u'The source of the article',
    )

    citation_id = zope.schema.TextLine(
        title=u'Citation Id',
        description=u'The unique identifier for this citation (such as Pubmed).',
    )

    citation_issued = zope.schema.TextLine(
        title=u'Citation Datetime',
        description=u'Taken from dcterms:issued.  Since the datetime format can be unpredictable, plain text is used.',
    )

    keywords = zope.schema.List(
        title=u'Keywords',
        description=u'The keywords of this model.',
    )


class IOpenCellSessionNote(zope.interface.Interface):
    """\
    OpenCell Session Note
    """

    filename = zope.schema.Choice(
        title=u'Session File',
        description=u'The session file that is made for this file.',
        vocabulary='ManifestListVocab',
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
