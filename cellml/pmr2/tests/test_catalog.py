import unittest

import zope.component
import zope.interface

from pmr2.app.exposure.interfaces import IExposure
from pmr2.app.exposure.interfaces import IExposureFile

from cellml.pmr2.catalog import *


class IDummy(zope.interface.Interface):
    """ dummy marker interface """


class Dummy(object):
    zope.interface.implements(IDummy)

    title = ''
    description = ''

    def __init__(self, *a, **kw):
        for k, v in kw.iteritems():
            setattr(self, k, v)

    def Title(self):
        return self.title

    def Description(self):
        return self.description


class DummyCmeta(object):
    zope.component.adapts(Dummy)

    def __init__(self, dummy):
        self.dummy = dummy

    @property
    def citation_title(self):
        return self.dummy.Title()

    @property
    def model_title(self):
        return 'Model Title: %s' % self.citation_title


class CatalogIndexTestCase(unittest.TestCase):

    def setUp(self):
        zope.component.provideAdapter(
            adapts=(IDummy,),
            provides=zope.interface.Interface,
            factory=DummyCmeta,
            name='cmeta',
        )

    def tearDown(self):
        pass

    def test_cmeta_citation_title_keyword_0001(self):
        obj = Dummy(title='Test Citation Title')
        result = cmeta_citation_title_keyword(obj)()
        self.assertEqual(result, ['test', 'citation', 'title'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CatalogIndexTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()

