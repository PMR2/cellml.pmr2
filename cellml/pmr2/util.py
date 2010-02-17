uri_prefix = {
    'info:pmid/': 'http://www.ncbi.nlm.nih.gov/pubmed/%s',
    'urn:miriam:pubmed:': 'http://www.ncbi.nlm.nih.gov/pubmed/%s',
}

def uri2http(uri):
    """\
    Resolves an info-uri into an http link based on the lookup table 
    above.
    """

    # XXX need a way to normalize these uris into string
    try:
        uri = str(uri)
    except:
        uri = uri.decode('utf8', 'replace')

    for k, v in uri_prefix.iteritems():
        if uri.startswith(k):
            return v % uri[len(k):]
    return None

def normal_kw(input):
    """\
    Method to normalize keywords so we don't have to deal with cases
    when searching and allow the usage of spaces to delimit terms.
    """

    return input.strip().replace(' ', '_').lower()
