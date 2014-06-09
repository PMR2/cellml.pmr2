import unittest
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from cellml.pmr2.tests.layer import CELLML_BASE_INTEGRATION_LAYER


class RegistryTestCase(unittest.TestCase):

    layer = CELLML_BASE_INTEGRATION_LAYER

    def test_set_registry(self):
        registry = getUtility(IRegistry)
        registry['cellml.pmr2.vhost.prefix_maps'] = {u'nohost': u'/plone'}
        self.assertEqual(registry['cellml.pmr2.vhost.prefix_maps'],
            {u'nohost': u'/plone'})


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RegistryTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()

