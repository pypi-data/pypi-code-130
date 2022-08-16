import loggerutility as logger

class Postgress:
    def getConnection(self, dbDetails):
        logger.log(f"Called Postgress getConnection.", "0")