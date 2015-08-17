import zope.component
from logging import getLogger

from Products.CMFCore.utils import getToolByName

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.settings import PMR2GlobalSettings

def cellml_pmr2_v0_6(context):
    """\
    Migration specific to CellML repository.

    This is for pmr2.app-0.6.
    """

    import traceback
    from zope.component.hooks import getSite
    logger = getLogger('cellml.pmr2')

    try:
        from cellml.pmr2 import _migration
    except ImportError:
        logger.error('Not all dependencies are available.')
        return

    # Set up the PMR1 curation flags.
    _migration.setup_pmr1_curation_flags()

    # Get all exposure files and migrate.
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='ExposureFile')
    for b in brains:
        file = b.getObject()
        try:
            _migration.migrate_curation_to_exposurefile(file)
        except:
            logger.error('Could not migrate curation for %s' % b.getPath())
            logger.warning(traceback.format_exc())


def cellml_cmeta_rdflib_fix(context):
    """
    Remove instances of `rdflib.Literal` in the cmeta notes.
    """

    logger = getLogger('cellml.pmr2')

    def check(item):
        if isinstance(item, (list, tuple)):
            for i in item:
                if not check(i):
                    return False
        return not item.__class__.__name__ == 'Literal'


    from cellml.pmr2.interfaces import ICmetaNote
    from cellml.pmr2.cmeta import mkstring
    attributes = ICmetaNote.names()

    path = ''

    results = context.portal_catalog(path=path, portal_type="ExposureFile")
    count = 0
    for b in results:
        try:
            note = zope.component.getAdapter(b.getObject(), name='cmeta')
        except:
            logger.error('`rdflib.Literal.Literal` must exist to run')
            break

        good = True
        for a in attributes:
            v = getattr(note, a)
            if not check(v):
                if a == 'citation_authors':
                    logger.warning('fixing:<%s>.%s: %s', b.getPath(), a, v)
                    fixed = [tuple(mkstring(names)) for names in v]
                    setattr(note, a, fixed)
                else:
                    logger.warning('error:<%s>.%s: %s', b.getPath(), a, v)
                good = False
        if not good:
            count += 1

    if count:
        logger.warning('%d failed.', count)
