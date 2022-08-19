import requests
from typing import Generator
from .seloger_search_query import SelogerSearchQuery
from ..real_estate import RealEstate
from ..real_estate_service import RealEstateService
from ..settings import settings
from ..target import Target

class SelogerService(RealEstateService):
    def __init__(self, api_key: str) -> None:
        self.url = settings.seloger_url
        self.session = requests.Session
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": settings.seloger_host
        }
    
    def search(self, query: SelogerSearchQuery) -> Generator[list[RealEstate]]:
        retrieve_page = lambda: self.session.get(
            self.url,
            headers=self.headers,
            params=query.dict()
        )

        total: int = retrieve_page().json()['totalCount']     
        num_pages: int = total // settings.page_size

        for page in range(2, num_pages + 1):
            query.pageIndex = page

            yield RealEstate.from_response(retrieve_page(), Target.SELOGER)
