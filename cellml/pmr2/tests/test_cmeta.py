import unittest
import os
from os.path import dirname, join
from cStringIO import StringIO

import rdflib

from cellml.pmr2.cmeta import *

testroot = dirname(__file__)
input_dir = join(testroot, 'input')
output_dir = join(testroot, 'output')

class CmetaTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_0000_basic(self):
        f = open(join(input_dir, 'beeler_reuter_model_1977.cellml'))
        cmeta = Cmeta(f)
        # instantiated.

    def test_0010_root_cmetaid(self):
        f = open(join(input_dir, 'beeler_reuter_model_1977.cellml'))
        cmeta = Cmeta(f)
        self.assertEqual(cmeta.root_cmetaid,
            'beeler_reuter_mammalian_ventricle_1977')

    def test_0011_nod_cmeta_id(self):
        f = open(join(input_dir, 'example_model_no_cmetaid.cellml'))
        cmeta = Cmeta(f)
        self.assertEqual(cmeta.root_cmetaid, None)

    def test_0020_cmeta_id(self):
        f = open(join(input_dir, 'example_model.cellml'))
        cmeta = Cmeta(f)
        self.assertEqual(cmeta.root_cmetaid, 'complex_model')
        # returns the cmeta:id in the order they showed up
        self.assertEqual(cmeta.get_cmetaid(), 
            ['complex_model', 'interface', 'membrane_potential'])

    def test_0021_cmeta_id(self):
        # TODO implement test for no cmeta:id for root model node
        # if the first item in get_cmetaid will always reference root
        # model node.
        pass

    def test_0030_cmeta_citation(self):
        f = open(join(input_dir, 'example_model.cellml'))
        cmeta = Cmeta(f)
        # returns the cmeta:id in the order they showed up
        ids = cmeta.get_cmetaid()
        citation = cmeta.get_citation(ids[0])
        self.assertEqual(citation[0]['pubmed_id'], '1111111111')
        self.assertEqual(citation[0]['title'], 'One Example Paper')
        self.assertEqual(citation[0]['journal'], 'Journal of Example Subject')
        self.assert_(isinstance(citation[0]['_id'], rdflib.BNode))
        self.assertEqual(len(citation[0]['creator']), 3)
        self.assertEqual(citation[0]['creator'][0]['family'], 'Family1')
        self.assertEqual(citation[0]['creator'][0]['given'], 'Given1')
        # XXX this is reversed somehow
        self.assert_('X' in citation[0]['creator'][0]['other'])
        self.assert_('Y' in citation[0]['creator'][0]['other'])
        self.assert_('Z' in citation[0]['creator'][0]['other'])
        self.assertEqual(citation[0]['creator'][1]['family'], 'Family2')
        self.assertEqual(citation[0]['creator'][2]['family'], 'Family2')
        self.assertEqual(citation[0]['creator'][2]['given'], 'H')

    def test_0031_cmeta_citation(self):
        # this one tests the namespace where the cellml namespace prefix
        # is not defined.
        f = open(join(input_dir, 
                      'noble_varghese_kohl_noble_1998_variant03.cellml'))
        cmeta = Cmeta(f)
        # returns the cmeta:id in the order they showed up
        ids = cmeta.get_cmetaid()
        citation = cmeta.get_citation(ids[0])
        self.assertEqual(citation[0]['pubmed_id'], '9487284')
        self.assertEqual(citation[0]['title'], 'Improved guinea-pig ventricular cell model incorporating a diadic space, IKr and IKs, and length- and tension-dependent processes')
        self.assertEqual(citation[0]['journal'], 'Canadian Journal of Cardiology')
        self.assert_(isinstance(citation[0]['_id'], rdflib.URIRef))
        self.assertEqual(len(citation[0]['creator']), 4)

    def test_0032_cmeta_citation_no_author(self):
        f = open(join(input_dir, 'example_model_no_author.cellml'))
        cmeta = Cmeta(f)
        # returns the cmeta:id in the order they showed up
        ids = cmeta.get_cmetaid()
        citation = cmeta.get_citation(ids[0])
        self.assertEqual(citation[0]['pubmed_id'], '1111111111')
        self.assertEqual(citation[0]['title'], 'One Example Paper')
        self.assertEqual(citation[0]['journal'], 'Journal of Example Subject')
        self.assert_(isinstance(citation[0]['_id'], rdflib.BNode))
        self.assertEqual(citation[0]['creator'], None)
        # XXX this is reversed somehow

    def test_0033_cmeta_citation_title_one_line(self):
        f = open(join(input_dir,
                      'baylor_hollingworth_chandler_2002_version12.cellml'))
        cmeta = Cmeta(f)
        # returns the cmeta:id in the order they showed up
        ids = cmeta.get_cmetaid()
        citation = cmeta.get_citation(ids[0])
        self.assertEqual(citation[0]['title'], 'Comparison of Simulated and Measured Calcium Sparks in Intact Skeletal Muscle Fibers of the Frog')

    def test_0040_keyword(self):
        f = open(join(input_dir, 'beeler_reuter_model_1977.cellml'))
        cmeta = Cmeta(f)
        answers = [
            ('#beeler_reuter_mammalian_ventricle_1977', 'ventricular myocyte'),
            ('#beeler_reuter_mammalian_ventricle_1977', 'electrophysiological'),
        ]
        keywords = cmeta.get_keywords()
        for a in answers:
            self.assert_(a in keywords, '%s not in keywords: %s' % 
                        (a, keywords))
        # done

    def test_0050_dc_vcard_info(self):
        f = open(join(input_dir, 'example_model.cellml'))
        cmeta = Cmeta(f)
        # returns the cmeta:id in the order they showed up
        creator = cmeta.get_dc_vcard_info(node='')
        self.assertEqual(len(creator), 1)
        self.assertEqual(creator[0]['family'], 'Family')
        self.assertEqual(creator[0]['given'], 'Given')
        self.assertEqual(creator[0]['orgname'], 'Example Organization')
        self.assertEqual(creator[0]['orgunit'], 'Example Subsidary')

    def test_0051_dc_vcard_info_missing_field(self):
        f = open(join(input_dir, 'example_model_creator_missing_field.cellml'))
        cmeta = Cmeta(f)
        creator = cmeta.get_dc_vcard_info(node='')
        self.assertEqual(creator[0]['family'], 'Family')
        self.assertEqual(creator[0]['orgunit'], 'Example Subsidary')

    def test_0052_dc_vcard_info_no_creator(self):
        f = open(join(input_dir, 'example_model_no_creator.cellml'))
        cmeta = Cmeta(f)
        # should not cause exception
        creator = cmeta.get_dc_vcard_info(node='')
        self.assertEqual(creator, [])

    def test_0053_dc_vcard_info_multi_creator(self):
        f = open(join(input_dir, 'example_model_multi_creator.cellml'))
        cmeta = Cmeta(f)
        creator = cmeta.get_dc_vcard_info(node='')
        self.assertEqual(len(creator), 2)
        # since query order is unsorted, we have to test as so
        family = [i['family'] for i in creator]
        family.sort()
        self.assertEqual(family, ['FirstFamily', 'SecondFamily'])

    def test_0051_dc_vcard_info_missing_field(self):
        f = open(join(input_dir, 'example_model_creator_missing_field.cellml'))
        cmeta = Cmeta(f)
        creator = cmeta.get_dc_vcard_info(node='')
        self.assertEqual(creator[0]['family'], 'Family')
        self.assertEqual(creator[0]['orgunit'], 'Example Subsidary')

    def test_0052_dc_vcard_info_no_creator(self):
        f = open(join(input_dir, 'example_model_no_creator.cellml'))
        cmeta = Cmeta(f)
        # should not cause exception
        creator = cmeta.get_dc_vcard_info(node='')
        self.assertEqual(creator, [])

    def test_0060_dcterms_license(self):
        # this file has the dcterms:license correctly encoded as url
        f = open(join(input_dir, 'example_model.cellml'))
        cmeta = Cmeta(f)
        license = cmeta.get_license()
        self.assertEqual(license, u'http://example.com/license')

    def test_0061_dcterms_license_literal(self):
        # this file has the dcterms:license incorrectly encoded as a
        # literal, but it should not matter.
        f = open(join(input_dir, 'example_model_no_cmetaid.cellml'))
        cmeta = Cmeta(f)
        license = cmeta.get_license()
        self.assertEqual(license, u'http://example.com/license')

    def test_0062_dcterms_license_missing(self):
        # this file has no dcterms:license.
        f = open(join(input_dir, 'example_model_no_creator.cellml'))
        cmeta = Cmeta(f)
        license = cmeta.get_license()
        self.assertEqual(license, None)

    def test_0070_dc_title(self):
        f = open(join(input_dir, 'example_model.cellml'))
        cmeta = Cmeta(f)
        titles = cmeta.get_dc_title(node='')
        title = titles[0]
        self.assertEqual(len(titles), 1)
        self.assertEqual(title, u'Model Title')
        self.assert_(isinstance(title, unicode))

    def test_0071_dc_title_no_creator(self):
        f = open(join(input_dir, 'example_model_no_creator.cellml'))
        cmeta = Cmeta(f)
        title = cmeta.get_dc_title(node='')
        self.assertEqual(title, None)

    def test_0072_dc_title_only(self):
        f = open(join(input_dir, 'example_model_top_title_only.cellml'))
        cmeta = Cmeta(f)
        titles = cmeta.get_dc_title(node='')
        title = titles[0]
        self.assertEqual(len(titles), 1)
        self.assertEqual(title, u'Test Title')
        self.assert_(isinstance(title, unicode))

    def test_0100_detailed_citation_vcard(self):
        f = open(join(input_dir, 'detailed_citation.cellml'))
        cmeta = Cmeta(f)
        creator = cmeta.get_dc_vcard_info(node='')
        self.assertEqual(len(creator), 1)
        self.assertEqual(creator[0]['family'], 'Author')
        self.assertEqual(creator[0]['given'], 'Main')
        self.assertEqual(creator[0]['orgname'], '')
        self.assertEqual(creator[0]['orgunit'], '')

    def test_9100_bad_xml(self):
        f = open(join(input_dir, 'example_model_bad_xml.cellml'))
        self.assertRaises(XMLSyntaxError, Cmeta, f)

    def test_9101_bad_rdf(self):
        f = open(join(input_dir, 'example_model_bad_rdf.cellml'))
        self.assertRaises(RDFParserError, Cmeta, f)

    def test_9102_missing_ns(self):
        f = open(join(input_dir, 'example_model_missing_ns.cellml'))
        self.assertRaises(XMLSyntaxError, Cmeta, f)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CmetaTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()

