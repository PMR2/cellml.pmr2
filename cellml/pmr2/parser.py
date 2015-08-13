"""
Mostly a direct copy of rdflib.plugins.parser.rdfxml simply because the
classes are not structured in a way that can be overridden with ease via
inheritance.
"""

from xml.sax import make_parser
from xml.sax.saxutils import handler
from xml.sax.handler import ErrorHandler

from rdflib.plugins.parsers.rdfxml import RDFXMLParser
from rdflib.plugins.parsers.rdfxml import RDFXMLHandler
from rdflib.plugins.parsers.rdfxml import make_parser


def create_parser(target, store, rdfhandler=RDFXMLHandler):
    """
    I don't know why rdflib can't be strucutred so I can just override
    the RDFXMLHandler
    """

    parser = make_parser()
    try:
        # Workaround for bug in expatreader.py. Needed when
        # expatreader is trying to guess a prefix.
        parser.start_namespace_decl(
            "xml", "http://www.w3.org/XML/1998/namespace")
    except AttributeError:
        pass  # Not present in Jython (at least)
    parser.setFeature(handler.feature_namespaces, 1)
    rdfhandler_ins = rdfhandler(store)
    rdfhandler_ins.setDocumentLocator(target)
    # rdfhandler_ins.setDocumentLocator(_Locator(self.url, self.parser))
    parser.setContentHandler(rdfhandler_ins)
    parser.setErrorHandler(ErrorHandler())
    return parser


class RDFCmetaHandler(RDFXMLHandler):

    def node_element_end(self, name, qname):
        self.parent.object = self.current.subject


class RDFCmetaParser(RDFXMLParser):
    """
    Reverting changes that implemented corrected features in rdflib to
    its legacy incorrect versions to enable the parsing of incorrectly
    encoded RDF/XML content found in many legacy CellML files.
    """

    rdfhandler = RDFCmetaHandler

    def parse(self, source, sink, **args):
        """
        Literally copy and pasting because rdflib is badly structured.
        """

        self._parser = create_parser(source, sink, rdfhandler=self.rdfhandler)
        content_handler = self._parser.getContentHandler()
        preserve_bnode_ids = args.get("preserve_bnode_ids", None)
        if preserve_bnode_ids is not None:
            content_handler.preserve_bnode_ids = preserve_bnode_ids
        # # We're only using it once now
        # content_handler.reset()
        # self._parser.reset()
        self._parser.parse(source)
