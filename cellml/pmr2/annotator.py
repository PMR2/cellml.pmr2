from shutil import rmtree
from lxml import etree
import re
import tempfile
import os
import time
from os import listdir
from os.path import join, dirname, splitext
from cStringIO import StringIO
import cPickle as pickle

import zope.interface
import zope.component

from pmr2.app.factory import named_factory
from pmr2.app.annotation.interfaces import *
from pmr2.app.annotation.annotator import ExposureFileAnnotatorBase
from pmr2.app.annotation.annotator import PortalTransformAnnotatorBase
from pmr2.app.exposure.interfaces import IExposureSourceAdapter

from cellml.api.pmr2.interfaces import ICellMLAPIUtility

from cellml.pmr2.urlopener import PmrUrlOpener
from cellml.pmr2.urlopener import make_pmr_path
from cellml.pmr2.cmeta import Cmeta
from cellml.pmr2.interfaces import *

XSLT_SOURCE = join(dirname(__file__), 'xslt')
xsltpath = lambda x: join(XSLT_SOURCE, x)

mathmlc2p_xslt = etree.parse(xsltpath('mathmlc2p.xsl'))
re_date = re.compile('^[0-9]{4}(-[0-9]{2}){0,2}')
pmr_loader = PmrUrlOpener()


class CellMLMathAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'CellML Math Extraction'
    label = u'Mathematics'
    description = u''
    for_interface = ICellMLMathNote

    def maths(self):
        cu = zope.component.getUtility(ICellMLAPIUtility)
        sa = zope.component.queryAdapter(
            self.context, IExposureSourceAdapter)
        exposure, workspace, path = sa.source()
        modelfile = '%s/@@%s/%s/%s' % (workspace.absolute_url(),
            'rawfile', exposure.commit_id, path)
        target = make_pmr_path(
            '/'.join(workspace.getPhysicalPath()), exposure.commit_id, path)
        model = cu.loadModel(target, loader=pmr_loader)
        results = cu.extractMaths(model)
        return results

    def generate(self):
        def mathc2p(s):
            r = StringIO()
            t = etree.parse(StringIO(s))
            t.xslt(mathmlc2p_xslt).write(r)
            return r.getvalue()
        maths = self.maths()
        maths = [(k, [mathc2p(m) for m in v]) for k, v in maths]
        return (
            ('maths', maths),
        )

CellMLMathAnnotatorFactory = named_factory(CellMLMathAnnotator)


class CellMLCodegenAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'CellML Code Generation'
    label = u'Generated Code'
    description = u''
    for_interface = ICellMLCodegenNote

    def codegen(self):
        cu = zope.component.getUtility(ICellMLAPIUtility)
        sa = zope.component.queryAdapter(
            self.context, IExposureSourceAdapter)
        exposure, workspace, path = sa.source()
        target = make_pmr_path(
            '/'.join(workspace.getPhysicalPath()), exposure.commit_id, path)
        model = cu.loadModel(target, loader=pmr_loader)

        return cu.exportCeleds(model)

    def generate(self):
        return (
            ('code', dict(self.codegen())),
        )

CellMLCodegenAnnotatorFactory = named_factory(CellMLCodegenAnnotator)


class OpenCellSessionAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator,
                              IExposureFileEditAnnotator)
    title = u'OpenCell Session Link'
    label = u'Simulate using OpenCell'
    for_interface = IOpenCellSessionNote

    def generate(self):
        return ()

OpenCellSessionAnnotatorFactory = named_factory(OpenCellSessionAnnotator)


class OpenCORAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator,
                              IExposureFileEditAnnotator)
    title = u'OpenCOR Launch Link'
    label = u'Launch with OpenCOR'
    for_interface = IOpenCORNote

    def generate(self):
        return ()

OpenCORAnnotatorFactory = named_factory(OpenCORAnnotator)


class CmetaAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'Basic CellML Metadata'
    label = u'Model Metadata'
    for_interface = ICmetaNote

    def generate(self):

        def generate_citation():
            ids = metadata.get_cmetaid()
            if not ids:
                # got no cmetaid, assuming no CellML metadata present.
                return

            citation = metadata.get_citation(ids[0])
            if not citation:
                # no citation, do nothing.
                return

            result['citation_id'] = citation[0]['citation_id']
            # more than just journal
            result['citation_bibliographicCitation'] = citation[0]['journal']
            result['citation_title'] = citation[0]['title']

            # XXX ad-hoc sanity checking
            issued = citation[0]['issued']
            if isinstance(issued, basestring) and re_date.search(issued):
                result['citation_issued'] = issued
            else:
                result['citation_issued'] = u''

            authors = []
            if not citation[0]['creator']:
                # no authors, we do not need the last field.
                return

            for c in citation[0]['creator']:
                family = c['family']
                given = c['given']
                if c['other']:
                    other = ' '.join(c['other'])
                else:
                    other = ''
                fn = (family, given, other)
                authors.append(fn)

            result['citation_authors'] = authors

        def generate_keywords():
            result['keywords'] = metadata.get_keywords()

        def generate_model_title():
            model_title = metadata.get_dc_title(node='')
            if model_title:
                result['model_title'] = model_title[0]

        def generate_model_authorship():
            dcvc = metadata.get_dc_vcard_info(node='')
            if not dcvc:
                return
            # using only first one
            info = dcvc[0]
            result['model_author'] = '%s %s' % (info['given'], info['family'])
            result['model_author_org'] = \
                '%s, %s' % (info['orgunit'], info['orgname'])

        result = {}
        metadata = Cmeta(StringIO(self.input))

        generate_citation()
        generate_keywords()
        generate_model_title()
        generate_model_authorship()

        # annotators are expected to return a list of tuples.
        return result.items()

CmetaAnnotatorFactory = named_factory(CmetaAnnotator)
