import urlparse

from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from pmr2.app.workspace.interfaces import IStorage

from cellml.api.pmr2.urlopener import DefaultURLOpener


class PmrUrlOpener(DefaultURLOpener):
    """
    Opener that accepts pmr (zeo) local URIs.
    """

    def __init__(self):
        super(PmrUrlOpener, self).__init__()
        self.approved_protocol.append('pmr')

    def loadURL(self, location, headers=None):
        p = urlparse.urlparse(location)
        if not p.scheme == 'pmr':
            # standard urls.
            return super(PmrUrlOpener, self).loadURL(location, headers=headers)

        # Fragments for the location of the object to be loaded are
        # delimited by colons.  Shouldn't contain any colons in any of
        # them, but the filepath might so we limit splits to two.
        objpath, rev, filepath = p.path.split(':', 2)

        portal = getSite()
        workspace = portal.restrictedTraverse(objpath.split('/'))
        storage = IStorage(workspace)
        storage.checkout(rev)
        return storage.file(filepath)
