from plone.app.contentlisting.interfaces import IContentListing
from plone.app.search.browser import Search, quote_chars, EVER

from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFCore.utils import getToolByName
from Products.ZCTextIndex.ParseTree import ParseError


try:
    from Products.AdvancedQuery import Ge, Le, Eq, In, RankByQueries_Sum
    ADVANCED_QUERY = True
except ImportError:
    ADVANCED_QUERY = False


class CellMLSearch(Search):

    def results(self, query=None, batch=True, b_size=10, b_start=0):
        """\
        Based on Search.results from plone.app.search.

        Difference would be the usage of Products.AdvanceQuery.
        """

        # Don't fail.
        if not ADVANCED_QUERY:
            return super(CellMLSearch, self).results(
                query, batch, b_size, b_start)

        if query is None:
            query = {}

        if batch:
            b_start = int(b_start)

        base_query = self.base_filter_query(query)
        if base_query:
            adv_query = self.filter_advanced_query(base_query)
            adv_sort = self.sort_advanced_query(base_query)

        if base_query is None:
            results = []
        else:
            catalog = getToolByName(self.context, 'portal_catalog')
            try:
                results = catalog.evalAdvancedQuery(adv_query, adv_sort)
            except ParseError:
                return []

        results = IContentListing(results)
        if batch:
            results = Batch(results, b_size, b_start)
        return results

    def base_filter_query(self, query):
        # based on filter_query, but with substantial difference so not
        # subclassing the original method.

        request = self.request
        rawtext = text = query.get('SearchableText', None)
        if text is None:
            text = request.form.get('SearchableText', '')
        if not text:
            # Without text, the only meaningful case is Subject
            subjects = request.form.get('Subject')
            if not subjects:
                return
        else:
            rawtext = text = text.strip()
            if '*' not in text:
                text += '*'

        # Stuff text into all PMR2/CellML/Cmeta indexes.

        cmeta_indexes = (
            'pmr2_authors_family_name',
            # XXX ^ this will become
            # 'cmeta_authors_family_name', 
            'cmeta_citation_title_keyword',
            'cmeta_citation_publication_year',
        )

        if rawtext:
            searchkeys = rawtext.lower().split()

            for i in cmeta_indexes:
                query[i] = searchkeys

        # XXX this should be configurable
        query['pmr2_review_state'] = ['published']

        catalog = getToolByName(self.context, 'portal_catalog')
        # AdvancedQuery does not understand these other keywords
        # valid_keys = self.valid_keys + tuple(catalog.indexes())
        valid_keys = tuple(catalog.indexes())

        for k, v in request.form.items():
            # XXX not sure what facet is, aside from a deprecated 
            # product.
            # if v and ((k in valid_keys) or k.startswith('facet.')):
            if v and (k in valid_keys):
                query[k] = v

        if text:
            query['SearchableText'] = quote_chars(text)

        # don't filter on created at all if we want all results
        created = query.get('created')
        if created:
            if created.get('query'):
                if created['query'][0] <= EVER:
                    del query['created']

        # respect `types_not_searched` setting
        types = query.get('portal_type', [])
        if 'query' in types:
            types = types['query']
        query['portal_type'] = self.filter_types(types)

        # # respect effective/expiration date
        # query['show_inactive'] = False

        # respect navigation root
        if 'path' not in query:
            query['path'] = getNavigationRoot(self.context)
        return query

    def sort_advanced_query(self, query):
        # sorting - we handle that separately
        sort_on = self.request.form.get('sort_on', None)
        sort_order = self.request.form.get('sort_order', 'asc')
        catalog = getToolByName(self.context, 'portal_catalog')
        valid_keys = tuple(catalog.indexes())

        if sort_on in valid_keys:
            # AdvancedQuery is strict about these keys, assume ascending
            # order if order is not recongnized.
            if sort_order not in ('reverse', 'desc', 'asc'):
                sort_order = 'asc'
            sort_option = [(sort_on, sort_order)]
        else:
            sort_option = [RankByQueries_Sum(
                (In('pmr2_authors_family_name', 
                    query['pmr2_authors_family_name']), 20), 
                (In('cmeta_citation_publication_year', 
                    query['cmeta_citation_publication_year']), 15), 
                (In('cmeta_citation_title_keyword',
                    query['cmeta_citation_title_keyword']), 10), 
            )]

        return sort_option

    def filter_advanced_query(self, query):
        # convert the standard query into advanced query.

        and_keys = ('review_state', 'pmr2_review_state', 'portal_type', 
                    'path', 'created')

        and_query = []
        or_query = []

        # string the rest of the query together with OR
        for k, v in query.iteritems():
            if isinstance(v, list):
                stmt = In(k, v)
            elif isinstance(v, dict) or hasattr(v, 'keys'):
                # XXX Only handling ranges with min or max
                q = v.get('query', None)
                r = v.get('range', None)
                if q is None or r not in ('min', 'max'):
                    continue

                if r == 'min':
                    stmt = Ge(k, q)
                elif r == 'max':
                    stmt = Le(k, q)

                # ranges usually imply further constraints, so use and
                and_query.append(stmt)
                continue
            else:
                stmt = Eq(k, v)

            if k in and_keys:
                and_query.append(stmt)
            else:
                or_query.append(stmt)

        or_ = lambda a, b: a | b
        and_ = lambda a, b: a & b

        and_query.append(reduce(or_, or_query))

        return reduce(and_, and_query)

