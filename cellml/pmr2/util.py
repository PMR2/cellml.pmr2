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

