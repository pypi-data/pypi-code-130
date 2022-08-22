from .tables import *

class Query:
    def __init__(self):
        pass
    
    def ticker(self, ticker):
        with Session(engine) as session:
            query = session.query(Ticker).where(Ticker.ticker==ticker)
            return query.first()
        
    def cik(self, ticker):
        with Session(engine) as session:
            query = session.query(CIK.cik).join(Ticker).filter(Ticker.ticker==ticker)
        
            return query.first().cik

    def xtags(self, ticker):
        with Session(engine) as session:
            stmt = db.select(Ticker).where(Ticker.ticker == ticker)
            return session.scalars(stmt).one().xtag
    
    def xtag(self, ticker, xtag):
        with Session(engine) as session:
            stmt = db.select(XBRLTag).join(Ticker).where(Ticker.ticker==ticker).where(XBRLTag.xtag==xtag).order_by(db.asc(XBRLTag.year))
            return session.scalars(stmt).all()