import unittest
from os.path import dirname, join

import zope.component
from Products.CMFCore.utils import getToolByName
import pmr2.app

from plone.testing.z2 import ZSERVER_FIXTURE
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.interfaces import TEST_USER_ID
from plone.app.testing import helpers

from pmr2.app.workspace.content import Workspace
from pmr2.app.tests.layer import PMR2_FIXTURE
from pmr2.app.exposure.tests.layer import EXPOSURE_FIXTURE
from pmr2.app.workspace.tests.layer import WORKSPACE_BASE_FIXTURE

from pmr2.testing.base import TestRequest

from pmr2.mercurial.tests.layer import MERCURIAL_FIXTURE
from pmr2.mercurial.tests.layer import MERCURIAL_BASE_FIXTURE
from cellml.pmr2.tests.layer import CELLML_BASE_FIXTURE


class CellMLMercurialLayer(PloneSandboxLayer):

    defaultBases = (CELLML_BASE_FIXTURE, MERCURIAL_BASE_FIXTURE,
        WORKSPACE_BASE_FIXTURE,)

    def setUpPloneSite(self, portal):
        import pmr2.mercurial.tests
        from pmr2.app.settings.interfaces import IPMR2GlobalSettings
        from pmr2.app.workspace.content import Workspace
        from pmr2.mercurial.tests import util

        settings = zope.component.getUtility(IPMR2GlobalSettings)

        p = settings.createDir(portal.workspace)
        sources = join(dirname(__file__), 'hgcellmldemo.tgz')
        util.extract_archive(p, sources)

        def mkhg_workspace(name):
            w = Workspace(name)
            w.storage = u'mercurial'
            portal.workspace[name] = w

        mkhg_workspace('hg_buckettap')
        mkhg_workspace('hg_btdemo')


CELLML_MERCURIAL_FIXTURE = CellMLMercurialLayer()

CELLML_MERCURIAL_LAYER = IntegrationTesting(
    bases=(CELLML_MERCURIAL_FIXTURE,),
    name="cellml.pmr2:mercurial_integration",
)

CELLML_MERCURIAL_LIVE_LAYER = IntegrationTesting(
    bases=(CELLML_MERCURIAL_FIXTURE, ZSERVER_FIXTURE,),
    name="cellml.pmr2:mercurial_live_integration",
)
