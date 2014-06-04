import unittest
import doctest

from zope.component import testing
from Testing import ZopeTestCase as ztc

from cellml.pmr2.tests import base


def test_suite():
    return unittest.TestSuite([

        # General tests.
        ztc.ZopeDocFileSuite(
            'README.rst', package='cellml.pmr2',
            test_class=base.CellMLDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # Cataloging tests.
        ztc.ZopeDocFileSuite(
            'catalog.txt', package='cellml.pmr2',
            test_class=base.CellMLDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # Code viewer tests
        ztc.ZopeDocFileSuite(
            'browser/code.txt', package='cellml.pmr2',
            test_class=base.CellMLDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        doctest.DocTestSuite(
            module='cellml.pmr2.util',
            setUp=testing.setUp, tearDown=testing.tearDown
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
