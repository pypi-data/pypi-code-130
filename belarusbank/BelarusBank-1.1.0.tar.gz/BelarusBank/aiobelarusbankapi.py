import asyncio

import aiohttp
from fake_useragent import UserAgent


class AIOBelBankAPI:
    def __init__(self):
        self.headers = {'User-Agent': UserAgent().chrome}

    async def get_atms(self, city='', ATM_currency=''):
        """
        Возвращает информацию о банкоматах
        :param city: Город
        :param ATM_currency: Валюта банкомата
        :return: json
        """
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=f'https://belarusbank.by/open-banking/v1.0/atms?city={city}&ATM_currency={ATM_currency}',
                headers=self.headers)
            return await response.text()

    async def get_infobox(self, city=''):
        """
        Возвращает информацию об инфо-киосках
        :param city: Город
        :return: json
        """
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=f'https://belarusbank.by/api/infobox?city={city}',
                headers=self.headers)
            return await response.text()

    async def get_news(self, lang='ru'):
        """
        Возвращает список новостей банка
        :param lang: Язык (be, ru - по умолчанию)
        :return: json
        """
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=f'https://belarusbank.by/api/news_info?lang={lang}',
                headers=self.headers)
            return await response.text()

    async def get_courses(self, city=''):
        """
        Возвращает курсы валют в определённых городах
        :param city: Город
        :return: json
        """
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=f'https://belarusbank.by/api/kursExchange?city={city}',
                headers=self.headers)
            return await response.text()

    async def get_cards_courses(self):
        """
        Возвращает все курсы по карточкам банка
        :return: json
        """
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url='https://belarusbank.by/api/kurs_cards',
                headers=self.headers)
            return await response.text()

    async def get_metals(self, city=''):
        """
        Возвращает информацию о продаже мерных слитков драгоценных металлов
        во всех структурных подразделениях в определённом городе.
        :param city: Город
        :return: json
        """
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=f'https://belarusbank.by/api/getinfodrall?city={city}',
                headers=self.headers)
            return await response.text()

    async def get_gems(self, city=''):
        """
        Возвращает информацию о реализуемых драгоценных камнях
        во всех структурных подразделениях в определённом городе.
        :param city: Город
        :return: json
        """
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=f'https://belarusbank.by/api/getgems?city={city}',
                headers=self.headers)
            return await response.text()

    async def get_deposits(self, deposit_currency=''):
        """
        Возвращает информацию о вкладах, которые открываются
        в определённой валюте.
        :param deposit_currency: Валюта
        :return: json
        """
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=f'https://belarusbank.by/api/deposits_info?deposit_currency={deposit_currency}',
                headers=self.headers)
            return await response.text()

    async def get_credits(self, credit_type=''):
        """
        Возвращает информацию о кредитах определённого типа
        :param credit_type: Тип кредита. Подробнее - https://belarusbank.by/ru/33139/forDevelopers/api/kredit
        :return: json
        """
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=f'https://belarusbank.by/api/kredits_info?type={credit_type}',
                headers=self.headers)
            return await response.text()

    async def get_filials(self, city='', service=''):
        """
        Возвращает информацию о подразделениях банка
        :param city: Город
        :param service: Услуга. Подробнее - https://belarusbank.by/ru/33139/forDevelopers/api/filials#uslugi
        :return: json
        """
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=f'https://belarusbank.by/api/filials_info?city={city}&usluga={service}',
                headers=self.headers)
            return await response.text()
