from .ncbi_abstract_search import NcbiAbstractSearch


class NcbiSearchIpg(NcbiAbstractSearch):
    def __init__(self, **kwargs):
        super(NcbiSearchIpg, self).__init__(**kwargs)
        self.db = 'ipg'
        self.update_session()

    def get_post_data(self, page=1, **kwargs):
        page = kwargs.get('page', page)
        size = kwargs.get('size', self.size)
        return {
            'EntrezSystem2.PEntrez.Ipg.Ipg_ResultsPanel.Ipg_DisplayBar.PageSize': size,
            'EntrezSystem2.PEntrez.Ipg.Ipg_ResultsPanel.Entrez_Pager.CurrPage': page,
        }
