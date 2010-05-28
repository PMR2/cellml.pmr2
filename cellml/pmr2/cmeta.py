from cStringIO import StringIO
from datetime import date, datetime

import lxml
import rdflib

from pmr2.rdf.base import RdfXmlObject
from rdflib.exceptions import ParserError as RDFParserError
from lxml.etree import XMLSyntaxError

cellml_namespaces = [
    'http://www.cellml.org/cellml/1.0#',
    'http://www.cellml.org/cellml/1.1#',
]

base_nsmap = {
    'cmsim': 'http://www.cellml.org/metadata/simulation/1.0#',
    'bqs': 'http://www.cellml.org/bqs/1.0#',
    'cmeta': 'http://www.cellml.org/metadata/1.0#',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dcterms': 'http://purl.org/dc/terms/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'vCard': 'http://www.w3.org/2001/vcard-rdf/3.0#',
}


def mkstring(input, replace=None):
    if not input:
        return input
    result = []
    for i in input:
        if i:
            result.append(unicode(i).strip())
        elif i is not None:
            result.append(i)
        elif replace is not None:
            # i must be None here as per above
            result.append(replace)
    return result


class Cmeta(RdfXmlObject):
    """\
    The Metadata Class.

    This class provides methods which will return a easy to access
    object to get to the nodes.  One instance per CellML/XML input.
    """

    def __init__(self, input=None):
        super(Cmeta, self).__init__()
        # XXX to support old use case.
        if input is not None:
            self.parse(input)

    def _purge(self):
        super(Cmeta, self)._purge()
        self.__cmetaids = []
        self.__cmetaid_attribs = []
        self.nsmap = {}

    def parse(self, input):
        super(Cmeta, self).parse(input)

        # update the mapping with what we trust
        self.nsmap.update(base_nsmap)

        # determine CellML namespace to use
        cellml_ns_set = set([v for v in self.dom.getroot().nsmap.values() 
            if v and 'http://www.cellml.org/cellml/' in v])
        if len(cellml_ns_set) > 1:
            raise ValueError('CellML file with more than one CellML namespace '
                             'declared is unsupported')
        if not cellml_ns_set:
            # no CellML namespace defined.
            return
        cellml_ns = cellml_ns_set.pop()
        if cellml_ns not in cellml_namespaces:
            raise ValueError('`%s` is an invalid CellML namespace' % cellml_ns)

        # since we have CellML namespace, we grab cmetaid.
        self.nsmap['cellml'] = cellml_ns
        # grab all cmetaids.
        self.__cmetaid_attribs = self.dom.xpath(
            './/@cmeta:id', namespaces=self.nsmap)
        self.__cmetaids = [n.strip() for n in self.__cmetaid_attribs]
        # self.__cmetaid_map = [(n.strip(), n.getparent()) 
        #                       for n in self.__cmetaid_attribs]

    @property
    def cmetaids(self):
        return self.__cmetaids

    # XXX pmr2.processor.cmeta had this instead of the above property.
    def get_cmetaid(self):
        return self.__cmetaids

    # XXX pmr2.processor.cmeta had this in tests, largely unused.
    @property
    def root_cmetaid(self):
        model_tag = '{%s}model' % self.nsmap['cellml']
        nodes = [n for n in self.__cmetaid_attribs 
                 if n.getparent().tag == model_tag]
        if len(nodes) == 1:
            return nodes[0].strip()

    def query(self, q, initBindings={}):
        """\
        Shortcut to query to include the namespace map.
        """
        return self.graph.query(
            q, initBindings=initBindings, initNs=self.nsmap)

    # XXX pubmed_id should be deprecated in favor for a unified urn scheme
    citation_key = ['_id', 'pubmed_id', 'title', 'journal', 'volume', 
        'first_page', 'last_page', 'issued', 'creator']

    def get_citation(self, cmetaid=None, subject=None, preserve=False):
        """\
        Returns a list of citations.

        subject - the subject, in the form of a uri, from which citation 
                  will be queried from.
        cmetaid - the cmetaid, in the form of a string, from which 
                  citaiton will be queried from.

        The above parameters cannot be both specified.
        """

        if not (subject is None or cmetaid is None):
            raise ValueError('cannot specify both subject and cmetaid')

        if cmetaid is not None:
            if isinstance(cmetaid, basestring):
                subject = rdflib.URIRef('#' + cmetaid)
            else:
                subject = cmetaid
        if isinstance(subject, basestring):
            subject = rdflib.URIRef(subject)

        bindings = {
            rdflib.Variable("?node"): subject,
        }

        q = """\
        SELECT ?ref ?pmid ?title ?journal ?volume ?first_page ?last_page ?pdate
            ?croot
        WHERE {
            ?node bqs:reference ?ref .
            ?ref bqs:JournalArticle ?article .
            OPTIONAL { ?article dc:creator ?croot } .
            OPTIONAL { ?article bqs:Journal [ dc:title ?journal ] } .
            OPTIONAL { ?ref bqs:Pubmed_id ?pmid } .
            OPTIONAL { ?article dc:title ?title } .
            OPTIONAL { ?article bqs:volume ?volume } .
            OPTIONAL { ?article bqs:first_page ?first_page } .
            OPTIONAL { ?article bqs:last_page ?last_page } .
            OPTIONAL { ?article dcterms:issued [ dcterms:W3CDTF ?pdate ] } .
        }
        """
        result = []
        for i in (self.query(q, bindings)):
            rawvalues = list(i)
            if rawvalues[-1]:
                rawvalues[-1] = self.get_creators(rawvalues[-1])

            values = []
            for v in rawvalues:
                if isinstance(v, rdflib.Literal):
                    v = unicode(v).strip()  # encoding?
                    # since all of these literals will be represented 
                    # in html, extra spaces are meaningless.
                    if not preserve:
                        v = u' '.join(v.split()) 
                # not too sure how to handle rdflib.URIRef
                values.append(v)

            values = dict(zip(self.citation_key, values))

            # Converting pubmed id into miriam uri, stored in citation id
            values['citation_id'] = u'urn:miriam:pubmed:%s' % \
                                      values['pubmed_id']

            result.append(values)

        return result

    creators_key = ['family', 'given', 'other',]

    def get_creators(self, node=None):
        """\
        Returns a list of associated vcards for a creator.

        input node must be a dc:creator node with nested container.
        """

        bindings = {
            rdflib.Variable("?node"): node,
        }

        # two queries below grab the vCard first
        q = """\
        SELECT ?vcname
        WHERE {
            ?node ?li ?creator .
            ?creator bqs:Person ?person .
            ?person vCard:N ?vcname .
        }
        ORDER BY ?li
        """
        standard = list(self.query(q, bindings))

        q = """\
        SELECT ?vcname
        WHERE {
            ?node ?li ?creator .
            ?creator vCard:N ?vcname .
        }
        ORDER BY ?li
        """
        pmr = list(self.query(q, bindings))

        vcards = standard + pmr

        # since PMR used vCard:Other wrongly (without putting multiple
        # names in bags) this query is needed.

        vcard_family = """\
        SELECT ?family ?given
        WHERE {
            ?vcname vCard:Family ?family .
            OPTIONAL { ?vcname vCard:Given ?given } .
        }
        """

        vcard_other = """\
        SELECT ?other
        WHERE {
            ?vcname vCard:Other ?other .
        }
        """

        result = []
        #import pdb;pdb.set_trace()
        for n in vcards:
            bindings = {
                rdflib.Variable("?vcname"): n[0],
            }
            # XXX only care about the first one
            family = self.query(vcard_family, bindings).selected[0]
            # XXX should care about all of them
            other = self.query(vcard_other, bindings).selected
            family = mkstring(family)
            other = mkstring(other)
            family.append(other)
            d = dict(zip(self.creators_key, family))
            result.append(d)
        return result

    dc_vcard_info = ['title', 'family', 'given', 'orgname', 'orgunit',]

    def get_dc_vcard_info(self, node=None):
        """\
        Returns the set of information which might be found in models in
        PMR1.

        Additional fields include dc:title which will most likely be
        used for the title of the file.

        Input node must be the parent of the relevant set of nodes.
        """

        if isinstance(node, basestring):
            node = rdflib.URIRef(node)

        q = """\
        SELECT ?title ?family ?given ?name ?unit
        WHERE {
            ?node dc:creator ?creator .
            OPTIONAL { 
                ?node dc:title ?title 
            } .
            OPTIONAL {
                ?creator vCard:N ?vcname .
                OPTIONAL { ?vcname vCard:Family ?family } .
                OPTIONAL { ?vcname vCard:Given ?given } .
            } .
            OPTIONAL { 
                ?creator vCard:ORG ?vcorg .
                OPTIONAL { ?vcorg vCard:Orgname ?name } .
                OPTIONAL { ?vcorg vCard:Orgunit ?unit } .
            } .
        }
        """

        result = []
        bindings = {
            rdflib.Variable("?node"): node,
        }
        vcards = self.query(q, bindings).selected
        result = [dict(zip(self.dc_vcard_info, mkstring(i, u''))) 
                  for i in vcards]
        return result

    def get_dc_title(self, node=None):
        """\
        Returns the dc:title from the specified node.
        """

        if isinstance(node, basestring):
            node = rdflib.URIRef(node)

        q = """\
        SELECT ?title
        WHERE {
            ?node dc:title ?title .
        }
        """
        bindings = {
            rdflib.Variable("?node"): node,
        }

        results = [s.strip() for s in self.query(q, bindings).selected]
        if results:
            return results

    def get_comments(self, node=None):
        """\
        Retrieves all cmeta:comment value nodes within the graph.
        """

        q = """\
        SELECT ?cmetaid ?value
        WHERE {
            ?cmetaid cmeta:comment [ rdf:value ?value ] .
        }
        """
        return list(self.query(q))

    def get_keywords(self, node=None):
        """\
        Get the dc:subject from the bqs:reference.
        """

        q = """\
        SELECT ?cmetaid ?value
        WHERE {
            ?cmetaid bqs:reference ?bqs .
            ?bqs dc:subject [ rdf:value ?container ] .
            ?container ?li ?value .
        }
        """
        # XXX doing selection of *all* keywords within the metadata 
        results = []
        for i in self.query(q):
            if isinstance(i[1], rdflib.Literal):
                results.append((str(i[0]), unicode(i[1]),))
        return results

    def get_license(self):
        """\
        Get the license information from the root node.
        """

        q = """\
        SELECT ?license
        WHERE {
            '' dcterms:license ?license .
        }
        """

        results = list(self.query(q))
        # We assume the first one
        if results:
            # should check for type, it shouldn't be literal but it can
            # be... so we ignore it for now.
            return results[0][0].encode('utf8', 'replace').strip()
