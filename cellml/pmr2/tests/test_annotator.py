from os.path import dirname, join
import unittest

from cellml.pmr2.annotator import *

testroot = dirname(__file__)
input_dir = join(testroot, 'input')

def read_file(fn):
    f = open(join(input_dir, fn))
    result = f.read()
    f.close()
    return result


class SimpleCmetaAnnotator(CmetaAnnotator):
    """
    Since we are skipping the whole registration of components 
    altogether here, we instantiate the annotator directly with the
    input changed to whatever we are trying to parse, so the context in
    our case is the actual content, thus the input property need to be 
    adjusted.
    """

    @property
    def input(self):
        return self.context


class CmetaAnnotatorTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def helper(self, fn, answers):
        f = read_file(fn)
        cmeta = SimpleCmetaAnnotator(f)
        results = cmeta.generate()
        # mangle results such that answers are predictable.
        results = dict(results)
        if 'keywords' in results:
            results['keywords'].sort()
        if 'citation_authors' in results:
            # other names are unsorted because of failure in the general
            # lack of usage of rdf:Seq, so we filter that out.
            results['citation_authors'] = [
                i[:2] for i in results['citation_authors']]
        self.assertEqual(results, answers)

    def test_0000_complete_data(self):
        self.helper('example_model.cellml', {
            'citation_authors': [
                (u'Family1', u'Given1'),
                (u'Family2', u'G'),
                (u'Family2', u'H'),
            ],
            'citation_bibliographicCitation': u'Journal of Example Subject',
            'citation_id': u'urn:miriam:pubmed:1111111111',
            'citation_issued': u'2004-04',
            'citation_title': u'One Example Paper',
            'keywords': [
                ('#complex_model', u'Ventricular Myocyte'),
                ('#complex_model', u'cardiac'),
                ('#complex_model', u'electrophysiology'),
            ],
            'model_author': u'Given Family',
            'model_author_org': u'Example Subsidary, Example Organization',
            'model_title': u'Model Title',
        })

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CmetaAnnotatorTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()

