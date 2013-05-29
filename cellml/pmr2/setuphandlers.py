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

