from logging import getLogger

import zope.component

from pmr2.app.exposure.interfaces import IExposureSourceAdapter

from pmr2.annotation.curation.interfaces import ICurationTool
from pmr2.annotation.curation.content import MasterCurationFlag
from pmr2.annotation.curation.content import CurationValue

logger = getLogger('cellml.pmr2._migration')


key_map = {
    u'pmr_cor_star': 'pmr1.cor',
    u'pmr_curation_star': 'pmr1.status',
    u'pmr_pcenv_star': 'pmr1.opencell',
    u'pmr_jsim_star': 'pmr1.jsim',
}

value_map = {
    u'0': 'c0',
    u'1': 'c1',
    u'2': 'c2',
    u'3': 'c3',
}

metadata_key = [u'cmeta', u'fieldml_metadata']

def setup_pmr1_curation_flags():
    """
    Flags for PMR1 compatibility.
    """

    curation = zope.component.queryUtility(ICurationTool)
    if not curation:
        logger.error('Cannot acquire curation tool.')
        return

    def curation_value(id_, title):
        value = CurationValue()
        # just local shortcuts.
        value.id = 'c' + id_
        value.title = title
        return value

    def master_flag(id, title, values):
        flag = MasterCurationFlag()
        flag.id = id
        flag.title = title
        flag.values = [curation_value(v, unicode(v)) for v in values]
        return flag

    values = (
        ('pmr1.status', u'Curation Status'),
        ('pmr1.opencell', u'OpenCell'),
        ('pmr1.cor', u'COR'),
        ('pmr1.jsim', u'JSim'),
    )

    for key, label in values:
        try:
            curation.addFlag(master_flag(key, label, list('0123')))
        except ValueError:
            logger.info('Curation flag `%s` already added', label)

def find_metadata(views):
    ii = 0

    for k in metadata_key:
        try:
            ii = views.index(k) + 1
            return ii
        except ValueError:
            continue

    return ii

def convert_curation(curation_items):
    if not curation_items:
        return {}

    result = {}
    for k, vs in curation_items:
        key = key_map.get(k, None)
        values = []
        for v in vs:
            value = value_map.get(v[0], None)
            if value:
                values.append(value)
        if key:
            result[key] = values

    return result

def migrate_curation_to_exposurefile(exposure_file):
    """
    Take an exposure file and plug in an annotation.
    """

    exposure = zope.component.getAdapter(exposure_file,
        IExposureSourceAdapter).exposure()

    if not exposure.curation:
        return

    bcuration = zope.component.getAdapter(exposure_file, name='basic_curation')
    bcuration.flags = convert_curation(exposure.curation.items())
    views = exposure_file.views

    target = find_metadata(views)
    views.insert(target, u'basic_curation')

    exposure_file.views = views
