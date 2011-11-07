import zope.component
import zope.interface
from plone.indexer.interfaces import IIndexer
from plone.indexer import indexer

from pmr2.app.exposure.interfaces import IExposure
from pmr2.app.exposure.interfaces import IExposureObject
from pmr2.app.exposure.interfaces import IExposureFile
from pmr2.app.exposure.interfaces import IExposureSourceAdapter

from cellml.pmr2.util import normal_kw

# Apply to all exposure objects

@indexer(IExposureObject)
def pmr1_citation_authors_sortable(context):
    if IExposure.providedBy(context):
        s = pmr1_citation_authors_exposure(context)()
    elif IExposureFile.providedBy(context):
        s = pmr1_citation_authors_exposurefile(context)()
    else:
        # well, this is either not an exposure type, or one that is
        # sitting in some place wrong - we ignore it.
        return ''
    if isinstance(s, basestring):
        return s.lower()
    return ''


# Apply to the root exposure object only

@indexer(IExposure)
def pmr1_citation_authors_exposure(context):
    return context.Title()

@indexer(IExposure)
def pmr1_citation_title_exposure(context):
    return context.Description()


# Apply to exposure files.

# XXX name should be cmeta_authors_family_name
@indexer(IExposureFile)
def pmr2_authors_family_name(context):
    note = zope.component.queryAdapter(context, name='cmeta')
    if not (note and note.citation_authors):
        return []
    return [normal_kw(i[0]) for i in note.citation_authors]

# XXX name should be cmeta_citation_title
@indexer(IExposureFile)
def pmr2_citation_title(context):
    note = zope.component.queryAdapter(context, name='cmeta')
    if not (note and note.citation_title):
        return []
    return normal_kw(note.citation_title)

@indexer(IExposureFile)
def pmr1_citation_authors_exposurefile(context):
    note = zope.component.queryAdapter(context, name='cmeta')
    if not (note and note.citation_authors and note.citation_issued):
        sa = zope.component.getAdapter(context, IExposureSourceAdapter)
        exposure = sa.exposure()
        if exposure is not None:
            workspace = exposure.workspace.split('/')[-1]
            return workspace.replace('_', ', ').title()
        return ''
    authors = u', '.join([i[0] for i in note.citation_authors])
    return u'%s, %s' % (authors, note.citation_issued[:4])

@indexer(IExposureFile)
def pmr1_citation_title_exposurefile(context):
    note = zope.component.queryAdapter(context, name='cmeta')
    if note:
        if note.model_title:
            return note.model_title
        elif note.citation_title:
            return note.citation_title
    return context.Title()

@indexer(IExposureFile)
def cmeta_citation_title_keyword(context):
    note = zope.component.queryAdapter(context, name='cmeta')
    if not (note and note.citation_title):
        return []
    return [normal_kw(i) for i in note.citation_title.split()]

@indexer(IExposureFile)
def cmeta_citation_publication_year(context):
    note = zope.component.queryAdapter(context, name='cmeta')
    if not (note and note.citation_issued):
        return []
    return [note.citation_issued[:4]]


# PMR2 Keyword Provider

def CmetaKeywordProvider(context):
    try:
        note = zope.component.queryAdapter(context, name='cmeta')
    except TypeError:
        return []
    if not (note and note.keywords):
        return []
    results = [normal_kw(i[1]) for i in note.keywords]
    results.sort()
    return results
