from pandas import DataFrame


class EliminateUnnecessaryData:
    def __init__(self, pd):
        self.pd = pd

    def process(self, dataframe: DataFrame) -> DataFrame:
        # dataframe = dataframe.loc[dataframe["referer"] == '"https://seb.ops1.thunderbees.com.br/sgi/"']
        clean_dataframe = dataframe.loc[dataframe["request"].str.contains("POST /access/authenticate", regex=True)]
        return clean_dataframe
