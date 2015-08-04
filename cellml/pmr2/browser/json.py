from cellml.pmr2.browser.view import CmetaNote, CellMLCodegenNote

from pmr2.json.mixin import JsonPage

from pmr2.json.collection.core import keyvalue_to_itemdata
from pmr2.json.collection.mixin import JsonCollectionPage


def cmeta_note_dict(cmeta_note):
    return {
        'title': cmeta_note.model_title,
        'model_author': cmeta_note.model_author,
        'model_author_org': cmeta_note.model_author_org,
        'citation_authors': cmeta_note.citation_authors,
        'citation_title': cmeta_note.citation_title,
        # a mismatch, but I blame the metadata spec.
        'citation_journal': cmeta_note.citation_bibliographicCitation,
        'citation_id': cmeta_note.citation_id,
        'keywords': cmeta_note.keywords,
    }

def cellml_codegen_links(form):
    results = {}
    for lang in form.available_langs():
        results[lang] = ('%s/%s/%s' %
            (form.context.absolute_url(), form.__name__, lang))
    return results

class JsonCmetaNote(JsonPage, CmetaNote):
    """
    Cmeta note.
    """

    def render(self):
        return self.dumps(cmeta_note_dict(self.note))


class JsonCellMLCodegenNote(JsonPage, CellMLCodegenNote):
    """
    Code generation.
    """

    def render(self):
        if self.language:
            return self.dumps({self.language: self.content()})

        results = cellml_codegen_links(self)
        return self.dumps(results)


class JsonCollectionCmetaNote(JsonCollectionPage, CmetaNote):
    """
    Cmeta note.
    """

    def update(self):
        super(JsonCollectionCmetaNote, self).update()
        self._jc_items = [keyvalue_to_itemdata(cmeta_note_dict((self.note)))]


class JsonCollectionCellMLCodegenNote(JsonCollectionPage, CellMLCodegenNote):
    """
    Code generation.
    """

    def update(self):
        super(JsonCollectionCellMLCodegenNote, self).update()
        if self.language:
            self._jc_items = [keyvalue_to_itemdata(
                {self.language: self.content()}
            )]
        else:
            self._jc_links = cellml_codegen_links(self)
