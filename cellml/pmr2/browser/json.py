from cellml.pmr2.browser.view import CmetaNote, CellMLCodegenNote
from pmr2.json.mixin import JsonPage


class JsonCmetaNote(JsonPage, CmetaNote):
    """
    Cmeta note.
    """

    def render(self):
        return self.dumps({
            'title': self.note.model_title,
            'model_author': self.note.model_author,
            'model_author_org': self.note.model_author_org,
            'citation_authors': self.note.citation_authors,
            'citation_title': self.note.citation_title,
            # a mismatch, but I blame the metadata spec.
            'citation_journal': self.note.citation_bibliographicCitation,
            'citation_id': self.note.citation_id,
            'keywords': self.note.keywords,
        })


class JsonCellMLCodegenNote(JsonPage, CellMLCodegenNote):
    """
    Code generation.
    """

    def render(self):
        if self.language:
            return self.dumps({self.language: self.content()})

        results = {}
        for lang in self.available_langs():
            results[lang] = ('%s/%s/%s' %
                (self.context.absolute_url(), self.__name__, lang))

        return self.dumps(results)
