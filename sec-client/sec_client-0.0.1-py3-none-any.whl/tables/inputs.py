from .tables import *
from .outputs import *
from utils import zipper


class Inserter:
    def __init__(self):
        pass

    def ticker(self, ticker, cik, company=""):
        with Session(engine) as session:
            ticker = Ticker(ticker=ticker, company=company, cik=[CIK(cik=cik)])
            session.add(ticker)

            session.commit()

    def value(self, ticker: str, xtag: str, value: int, year: int, line_item="", statement=""):
        with Session(engine) as session:
            stmt = db.select(Ticker).where(Ticker.ticker == ticker)
            obj = session.scalars(stmt).one()
            obj.xtag.append(
                XBRLTag(
                    xtag=xtag, value=value, year=year, line_item=[LineItem(line_item=line_item, statement=statement)]
                )
            )
            session.commit()


class Updater:
    def __init__(self):
        pass

    def ticker(self, ticker: str, cik: int, company=""):
        with Session(engine) as session:
            query = session.query(CIK).where(Ticker.ticker == ticker).first()
            query.cik = cik
            session.add(query)
            session.commit()

    def tags(self, ticker: str, tags: list):
        query = Query().get_ticker(ticker)
        with Session(engine) as session:
            query.xtag.extend(tags)
            session.commit()

    def statement(self, xtag, statement):
        # sourcery skip: class-extract-method
        with Session(engine) as session:
            stmt = db.select(LineItem).join(XBRLTag).where(XBRLTag.xtag == xtag)
            obj = session.scalars(stmt).all()

            for _ in obj:
                _.statement = statement

            session.commit()

    def line_item(self, xtag, line_item):
        with Session(engine) as session:
            stmt = db.select(LineItem).join(XBRLTag).where(XBRLTag.xtag == xtag)
            obj = session.scalars(stmt).all()

            for _ in obj:
                _.line_item = line_item

            session.commit()