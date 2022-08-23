from asclepius.instelling import Instelling, GGZ, ZKH
from asclepius.medewerker import Medewerker
from asclepius.portaaldriver import PortaalDriver
from asclepius.auxhilary import check_input

# import other dependencies
from pandas.core.frame import DataFrame
from pandas import ExcelWriter
from pandas import read_excel, merge, isnull
from numpy import nan as numpy_nan

class TestExcel:

    def __init__(self, join_col: str, header_row: int = 0, test_cols: list = None):
        self.join_col = join_col
        self.header_row = header_row
        self.test_cols = test_cols
        return None

    def __str__(self) -> str:
        kolommen = ", ".join(self.test_cols)
        return f'TestExcelInfo\nJoin Kolom: {self.join_col}\nHeader regel: {self.header_row}\nKolommen: {kolommen}'

    def __repr__(self) -> str:
        return self.__str__()

    def excels_vergelijken(self, instelling: GGZ):
        '''
        Deze functie vergelijkt de excel uit de A omgeving met de excel uit de P omgeving.
        '''

        # Maak een join van de A en P excels
        instelling.prestatiekaart = self.join_excels(instelling.excel_a, instelling.excel_p)        

        # Check het aantal regels in A en in P
        lengte_a, lengte_p = self.aantal_indicatoren(instelling.prestatiekaart)
        
        self.check_existence(instelling)
        
        self.check_empty(instelling)

        self.check_columns(instelling)

        self.conclusie(instelling, lengte_a, lengte_p)
        return None

    def join_excels(self, excel_a, excel_p) -> DataFrame:
        # Import excelsheets
        data_a = read_excel(excel_a, index_col = None, header = self.header_row)
        data_p = read_excel(excel_p, index_col = None, header = self.header_row)

        columns_a = data_a.columns.values.tolist()
        columns_p = data_p.columns.values.tolist()

        for column in self.test_cols + [self.join_col]:
            
            # Check of de te testen kolom in de A excel staat
            if column not in columns_a:
                raise Exception(f'De kolom {column} bestaat niet in de excel uit de A omgeving.')

            # Check of de te testen kolom in de P excel staat
            if column not in columns_p:
                raise Exception(f'De kolom {column} bestaat niet in de excel uit de P omgeving.')

        for column in columns_a:
            if column == self.join_col:
                pass
            elif column not in self.test_cols:
                # Drop kolommen die niet getest hoeven worden uit A
                data_a = data_a.drop(columns=[column])
                columns_a.remove(column)
            else:
                new_name = f'{column}_a'
                data_a = data_a.rename(columns={column: new_name})
        
        for column in columns_p:
            if column == self.join_col:
                pass
            elif column not in self.test_cols:
                # Drop kolommen die niet getest hoeven worden uit P
                data_p = data_p.drop(columns=[column])
                columns_p.remove(column)
            else:
                new_name = f'{column}_p'
                data_p = data_p.rename(columns={column: new_name})
        
        self.columns_a = [f'{column}_a' for column in columns_a if column != self.join_col]
        self.columns_p = [f'{column}_p' for column in columns_p if column != self.join_col]

        # voeg index column toe
        data_a['index_a'] = data_a.index
        data_p['index_p'] = data_p.index

        # join dataframes op titlel
        wrangled_data = merge(data_a, data_p, how = 'outer', on = self.join_col)
        wrangled_data.fillna(value = numpy_nan)
        
        # return de prestatiekaart data
        return wrangled_data

    def check_existence(self, instelling: GGZ) -> None:
        prestatiekaart = instelling.prestatiekaart
        # Checkt of een titel niet in A bestaat, niet in P bestaat
        for i in range(len(prestatiekaart)):
            if isnull(prestatiekaart.at[i, 'index_a']):
                omgeving = 'A'
            elif isnull(prestatiekaart.at[i, 'index_p']):
                omgeving = 'P'
            else:
                # ga door met de volgende loop
                continue

            instelling.nieuwe_bevinding(prestatiekaart.at[i, self.join_col], column = 'Alle', bevinding = f'Indicator niet in {omgeving} portaal.')
            prestatiekaart = prestatiekaart.drop(index = i)

        # Reset de indices (omdat we rijen gedropt hebben)
        prestatiekaart = prestatiekaart.reset_index(drop = True)
        instelling.prestatiekaart = prestatiekaart
        return None

    def check_empty(self, instelling: GGZ) -> None:
        prestatiekaart = instelling.prestatiekaart

        # Iterate over all rows in the dataframe
        for i in range(len(prestatiekaart)):
            
            # Check of de indicator niet helemaal leeg is in A en P
            all_colls_empty = True
            for column in self.columns_a + self.columns_p:
                if not isnull(prestatiekaart.at[i, column]):
                    all_colls_empty = False
                    break
                   
            if all_colls_empty:
                # Als alle kolommen leeg zijn voegen we dat toe als bevindingen
                instelling.nieuwe_bevinding(prestatiekaart.at[i, self.join_col], column = 'Alle', bevinding = 'Indicator is leeg in beide portalen.')
                prestatiekaart = prestatiekaart.drop(index = i)
                
                # Ga verder met de volgende rij
                continue

            # Check which of the test columns are empty
            for omgeving in ['A', 'P']:
                if omgeving == 'A':
                    columns = self.columns_a
                elif omgeving == 'P':
                    columns = self.columns_p
                
                for column in columns:
                    if isnull(prestatiekaart.at[i, column]):
                        instelling.nieuwe_bevinding(prestatiekaart.at[i, self.join_col], column = column[:-2], bevinding = f'Kolom {column[:-2]} leeg in {omgeving} portaal.')
                    
        prestatiekaart = prestatiekaart.reset_index(drop = True)
        instelling.prestatiekaart = prestatiekaart
        return None

    def check_columns(self, instelling: GGZ):

        prestatiekaart = instelling.prestatiekaart

        for column in self.test_cols:
            col_name_a = f'{column}_a'
            col_name_p = f'{column}_p'

            for i in range(len(prestatiekaart)):
                if isnull(prestatiekaart.at[i, col_name_a]) and isnull(prestatiekaart.at[i, col_name_p]):
                    pass

                # Check of de kolom gelijk is in het A en P portaal
                elif not (prestatiekaart.at[i, col_name_a] == prestatiekaart.at[i, col_name_p]):
                    instelling.nieuwe_bevinding(prestatiekaart.at[i, self.join_col], column = column, a = str(prestatiekaart.at[i, col_name_a]), p = str(prestatiekaart.at[i, col_name_p]), bevinding = 'A wijkt af van P.')
        
        instelling.prestatiekaart = prestatiekaart
        return None

    def aantal_indicatoren(self, prestatiekaart: DataFrame):
        lengte_a = prestatiekaart['index_a'].max() + 1
        lengte_p = prestatiekaart['index_p'].max() + 1
        return lengte_a, lengte_p

    def conclusie(self, instelling: GGZ, lengte_a: int, lengte_p: int):
        bevindingen = instelling.bevindingen
        lengte_bevingingen = len(bevindingen)

        instelling.nieuwe_bevinding('', '', '')
        instelling.nieuwe_bevinding('Aantal indicatoren in Prestatiekaart:', column = '', a = str(lengte_a), p = str(lengte_p), bevinding = '')
        instelling.nieuwe_bevinding('Totaal aantal bevindingen:', column = '', bevinding = str(lengte_bevingingen))
        return None


class RegressieTest:
    def __init__(self, gebruiker: Medewerker, product: str = 'custom', test_excel: TestExcel = None, target_link: str = None, download_link: str = None, variabele_links: DataFrame = None) -> None:

        check_input(gebruiker, product, target_link, download_link, variabele_links)
            
        # Initialiseren
        self.gebruiker = gebruiker
        self.portaaldriver = PortaalDriver(self.gebruiker, product, target_link, download_link, variabele_links)
        self.testfuncties = test_excel
        self.product = product

        return None

    def __str__(self) -> str:
        return f'RegressieTest\nGebruiker: {self.gebruiker}'

    def __repr__(self) -> str:
        return self.__str__()

    def test(self, *instellingen: GGZ):
        '''
        Voer de regressietest uit op de opgegeven instellingen.

        Parameters
        ----------
        instellingen : GGZ of ZKH
            De instellingen waarop de regressietest moet worden uitgevoerd. Gescheiden door komma's.

        Returns
        ----------
        None
            De functies geeft None als output, maar produceert wel een excel met de resultaten.
        '''
        
        mislukt = []
        for instelling in instellingen:
            
            # Download de benodigde Excelbestanden uit het portaal
            try:
                self.portaaldriver.webscraper(instelling)
            except Exception as ex:
                print(ex)
                mislukt.append(instelling.klant_code)

            # Vergelijk de gedownloade excels
            try:
                self.testfuncties.excels_vergelijken(instelling)
            except Exception as ex:
                print(ex)
                mislukt.append(instelling.klant_code)

        # Schrijf de resultaten weg als Excelbestand
        with ExcelWriter(f'Bevindingen Regressietest.xlsx') as writer:
            for instelling in instellingen:
                if instelling.klant_code not in mislukt:
                    instelling.bevindingen.to_excel(writer, sheet_name=f'{instelling.klant_code}')
                else: pass
        
        # Ontdubbelen van de lijst met mislukte tests
        mislukt = set(mislukt)

        # Print mislukte tests
        if len(mislukt) != 0:
            print('Mislukte regressietests:', ' '.join(mislukt))
        else:
            print('Geen mislukte regressietests!')
        return None


