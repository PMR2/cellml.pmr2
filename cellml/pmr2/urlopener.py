import urlparse

from zope.component import getUtility
from zope.component.hooks import getSite
from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName
from pmr2.app.workspace.interfaces import IStorage

from cellml.api.pmr2.urlopener import DefaultURLOpener


def external_to_url(kws):
    """
    Convert an external dict to a URI, either a standard HTTP URL for
    truly external instances, or an internal pmr: URI if internal.
    """

    p = urlparse.urlparse(kws['location'])
    # look up whether the netloc is a vhost that needs mangling.
    mappings = getUtility(IRegistry).get('cellml.pmr2.vhost.prefix_maps') or {}
    if not p.netloc in mappings:
        # XXX in theory another registry entry can resolve this, but
        # that whole thing should really be integrated into PMR proper
        # for the resolution of 'rawfile'
        kws['view'] = 'rawfile'
        return '%(location)s/%(view)s/%(rev)s/%(path)s' % kws

    kws['objpath'] = mappings[p.netloc] + p.path
    return 'pmr:%(objpath)s:%(rev)s:%(path)s' % kws


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
        pathinfo = storage.pathinfo(filepath)
        if pathinfo.get('external'):
            kws = {}
            kws.update(pathinfo['external'])
            target = external_to_url(kws)
            return self.loadURL(target)
        return storage.file(filepath)
