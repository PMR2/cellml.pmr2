import unittest
from os.path import dirname, join

import zope.component
from Products.CMFCore.utils import getToolByName
import pmr2.app

from plone.testing.z2 import ZSERVER
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing.interfaces import TEST_USER_ID
from plone.app.testing import helpers

from pmr2.app.workspace.content import Workspace
from pmr2.app.exposure.tests.layer import EXPOSURE_FIXTURE

from pmr2.testing.base import TestRequest


class CellMLBaseLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import cellml.pmr2
        import cellml.api.pmr2
        self.loadZCML(package=cellml.api.pmr2)
        self.loadZCML(package=cellml.pmr2)
        self.loadZCML('test.zcml', package=cellml.pmr2.tests)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'cellml.pmr2:default')

CELLML_BASE_FIXTURE = CellMLBaseLayer()

CELLML_BASE_INTEGRATION_LAYER = IntegrationTesting(
    bases=(CELLML_BASE_FIXTURE,),
    name="cellml.pmr2:basic_integration",
)


class CellMLExposureLayer(PloneSandboxLayer):

    defaultBases = (EXPOSURE_FIXTURE, CELLML_BASE_FIXTURE,)

    def mkAddWorkspace(self, container, id_):
        w = Workspace(id_)
        w.storage = 'dummy_storage'
        container[id_] = w

    def setUpPloneSite(self, portal):

        from pmr2.app.workspace.interfaces import IStorageUtility
        from pmr2.app.exposure.browser.browser import ExposureAddForm
        from pmr2.app.exposure.browser.browser import ExposureFileGenForm

        import pmr2.testing

        # instantiate test data on disk as dummy_storage backed
        # workspaces.
        su = zope.component.getUtility(IStorageUtility, name='dummy_storage')

        # TODO handle cleanup when that dummy provide support.
        su._loadDir('rdfmodel',
            join(dirname(pmr2.testing.__file__), 'data', 'rdfmodel'))

        su._loadDir('main_model', join(dirname(__file__), 'repo', 'main'))
        su._loadDir('demo_model', join(dirname(__file__), 'repo', 'impl'))
        # XXX the location can change!
        su._dummy_storage_data['demo_model'][0]['main'] = {
            '': '_subrepo',
            'rev': '0',
            'location': 'http://nohost/plone/workspace/main_model',
            # 'location': 'http://localhost:55001/plone/workspace/main_model',
        },

        # add workspace objects
        self.mkAddWorkspace(portal.workspace, 'rdfmodel')
        self.mkAddWorkspace(portal.workspace, 'main_model')
        self.mkAddWorkspace(portal.workspace, 'demo_model')

        # publish workspace objects
        helpers.setRoles(portal, TEST_USER_ID, ['Manager'])
        pw = getToolByName(portal, "portal_workflow")
        pw.doActionFor(portal.workspace['rdfmodel'], 'publish')
        pw.doActionFor(portal.workspace['main_model'], 'publish')
        helpers.setRoles(portal, TEST_USER_ID, ['Member', 'Authenticated',])

        # poke in an exposure
        request = TestRequest(form={
            'form.widgets.workspace': u'rdfmodel',
            'form.widgets.commit_id': u'2',
            'form.buttons.add': 1,
        })
        testform = ExposureAddForm(portal.exposure, request)
        testform.update()
        exp_id = testform._data['id']
        context = portal.exposure[exp_id]
        self.exposure1 = context
        rdfmodel = portal.workspace.rdfmodel
        self.file1 = u'example_model.cellml'
        request = TestRequest(
            form={
                'form.widgets.filename': [self.file1],
                'form.buttons.add': 1,
            })
        testform = ExposureFileGenForm(context, request)
        testform.update()
        # store this path for easy access by test case
        self['exposure_file1_path'] = context[self.file1].getPhysicalPath()

CELLML_EXPOSURE_FIXTURE = CellMLExposureLayer()

CELLML_EXPOSURE_INTEGRATION_LAYER = IntegrationTesting(
    bases=(CELLML_EXPOSURE_FIXTURE,),
    name="cellml.pmr2:exposure_all_integration",
)

CELLML_EXPOSURE_INTEGRATION_LIVE_LAYER = IntegrationTesting(
    bases=(ZSERVER, CELLML_EXPOSURE_FIXTURE,),
    name="cellml.pmr2:exposure_all_live_integration",
)
