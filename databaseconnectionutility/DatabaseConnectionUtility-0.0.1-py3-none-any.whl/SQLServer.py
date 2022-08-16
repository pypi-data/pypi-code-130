import loggerutility as logger

class SQLServer:
    def getConnection(self, dbDetails):
        logger.log(f"Called SQLServer getConnection.", "0")