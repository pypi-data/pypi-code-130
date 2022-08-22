from .ncbi_abstract_search import NcbiAbstractSearch


class NcbiSearchProtein(NcbiAbstractSearch):
    def __init__(self, **kwargs):
        super(NcbiSearchProtein, self).__init__(**kwargs)
        self.db = 'protein'
        self.update_session()

    def get_post_data(self, page=1, **kwargs):
        page = kwargs.get('page', page)
        size = kwargs.get('size', self.size)
        return {
            'EntrezSystem2.PEntrez.Protein.Sequence_ResultsPanel.Sequence_DisplayBar.PageSize': size,
            'EntrezSystem2.PEntrez.Protein.Sequence_ResultsPanel.Entrez_Pager.CurrPage': page,
        }
