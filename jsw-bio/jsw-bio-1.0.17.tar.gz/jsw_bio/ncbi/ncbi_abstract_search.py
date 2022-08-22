import requests
import jsw_nx as nx

from bs4 import BeautifulSoup


# https://js.work/posts/a97e4e73abb6e


class NcbiAbstractSearch:
    def __init__(self, **kwargs):
        self.term = kwargs.get('term')
        self.size = kwargs.get('size', 20)
        self.last_query_key = '1'
        self.db = 'protein'
        self.session_id = None

    def update_session(self):
        url = f'https://www.ncbi.nlm.nih.gov/{self.db}?term={self.term}'
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        last_query_key_el = soup.select_one('[name="EntrezSystem2.PEntrez.DbConnector.LastQueryKey"]')
        self.last_query_key = last_query_key_el.attrs['value']
        self.session_id = res.headers.get('NCBI-SID')

    def get(self, page=1, **kwargs):
        data = self.get_post_data(page, **kwargs)
        data.update({
            'term': self.term,
            'EntrezSystem2.PEntrez.DbConnector.LastQueryKey': self.last_query_key,
            'EntrezSystem2.PEntrez.DbConnector.Cmd': 'PageChanged'
        })
        headers = {'cookie': f'ncbi_sid={self.session_id}'}
        res = requests.post(f'https://www.ncbi.nlm.nih.gov/{self.db}', data=data, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        el_title = soup.select_one('title')
        el_page = soup.select_one('[name="ncbi_pageno"]')
        val_title = el_title.text
        val_page = el_page.attrs['content']

        if nx.includes(val_title, self.term) and val_page == str(page):
            return self.get_ids(soup)
        else:
            self.update_session()
            return self.get(**kwargs)

    def get_post_data(self, page=1, **kwargs):
        page = kwargs.get('page', page)
        size = kwargs.get('size', self.size)
        return {
            'EntrezSystem2.PEntrez.Protein.Sequence_ResultsPanel.Ipg_DisplayBar.PageSize': size,
            'EntrezSystem2.PEntrez.Protein.Sequence_ResultsPanel.Entrez_Pager.CurrPage': page,
        }

    @classmethod
    def get_ids(cls, soup):
        anchors = soup.select('#maincontent .content .rprt .rslt .title a')
        ids = []

        for anchor in anchors:
            href = anchor.attrs['href']
            id = href.split('/')[-1]
            ids.append(id)
        return ids
