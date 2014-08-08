import unittest
import warnings

import zope.component

from zExceptions import Unauthorized
from Products.PloneTestCase.setup import portal_owner, default_password
from Products.PloneTestCase import ptc
from Products.Five.testbrowser import Browser
from plone.registry.interfaces import IRegistry

from cellml.pmr2.interfaces import IVHostRemap
from pmr2.testing.base import TestRequest

from cellml.pmr2.browser.vhost import VHostRemapEditForm


class VHostRemapFormTestCase(ptc.FunctionalTestCase):
    """
    Testing functionalities of forms that don't fit well into doctests.
    """

    def afterSetUp(self):
        self.registry = zope.component.getUtility(IRegistry)
        self.vhosts = self.registry.forInterface(IVHostRemap,
            prefix='cellml.pmr2.vhost')

        if not IVHostRemap['prefix_maps'].__name__ == 'prefix_maps':
            # XXX SOMETHING REALLY WENT WRONG somewhere in the setup
            # somewhere and I have no idea how/where that got set.
            # This apears to only happen in this test harness but NOT
            # during actual running, soooo....
            IVHostRemap['prefix_maps'].__name__ = 'prefix_maps'
            warnings.warn("IVHostRemap['prefix_maps'].__name__ got "
                "overwritten somewhere??")

    def test_basic_render_form(self):
        request = TestRequest()
        form = VHostRemapEditForm(self.portal, request)
        form.update()
        result = form.render()
        self.assertTrue(result)

    def test_edit_field(self):
        request = TestRequest(form={
            'form.widgets.prefix_maps': 'models.example.com /plone',
            'form.buttons.apply': 1,
        })
        form = VHostRemapEditForm(self.portal, request)
        form.update()
        result = form.render()
        self.assertEqual(self.vhosts.prefix_maps,
            {u'models.example.com': u'/plone'})

    def test_render_field(self):
        self.vhosts.prefix_maps = {
            u'models.example.org': u'/plone',
            u'models.example.com': u'/plone',
        }
        request = TestRequest()
        form = VHostRemapEditForm(self.portal, request)
        form.update()
        result = form.render()
        self.assertIn('models.example.com /plone\nmodels.example.org /plone',
            result)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(VHostRemapFormTestCase))
    return suite


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(VHostRemapFormTestCase))
    return suite
