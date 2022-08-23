# import hardcoded information from fileserver
import sys
sys.path.append(r'\\valuecare.local\fileserver\Algemeen\Automatisch testen\Python')
from parameters import HardCodedParameters

# import other dependencies
from pandas import DataFrame, concat

class Instelling:
    def __init__(self, klant_code: str):
        self.klant_code = klant_code
        self.baselink = ''
        self.huidige_omgeving = ''
        self.link_dict = ''

        self.target_link_ = ''
        self.target_link = ''

        self.download_link_ = ''
        self.download_link = ''


        # Test attributen
        self.excel_a = 'path naar excel_a bestand'
        self.excel_p = 'path naar excel_p bestand'
        self.prestatiekaart = DataFrame()

        # Initialiseer een DataFrame waarin we alle bevindingen kunnen opslaan
        self.bevindingen = DataFrame({'Indicator': [], 'Kolom': [], 'A': [], 'P': [], 'Bevinding': []})
        return None
    
    def update_baselink(self):
        # baselink
        self.baselink = HardCodedParameters.baselink + self.huidige_omgeving[0] + self.klant_code + '/portaal/'

        # login link
        self.login = self.baselink + 'login'

        # links
        self.target_link = self.baselink + self.target_link_
        self.download_link = self.baselink + self.download_link_
        return None

    def link_setter(self, target_link, download_link, variabele_links) -> None:
        '''
        Deze functie bouwt de correcte links voor een instelling.
        '''

        # stel variabele links in
        if (type(variabele_links) != type(None)):
            print(self.klant_code + ' in var links!')
            self.target_link_ = variabele_links['bi_prestatiekaart'].at[self.klant_code]
            self.download_link_ = variabele_links['bi_excel_download'].at[self.klant_code]

        # anders de gewone custom links
        else:
            self.target_link_ = target_link
            self.download_link_ = download_link
        return None

    def kies_omgeving(self, omgeving: str):
        if omgeving == 'acceptatie':
            # verander huidige omgeving naar acceptatie
            self.huidige_omgeving = 'acceptatie'
        elif omgeving == 'productie':
            # verander huidige omgeving naar productie
            self.huidige_omgeving = 'productie'
        else:
            raise Exception('Geen geldige omgeving opgegeven.')
        
        self.update_baselink()
        return None
    
    def genereer_nieuwe_naam(self, product: str, test: bool = False):
        if test:
            new_name = f'{self.klant_code}_{product}_{self.huidige_omgeving[0]}_test.xlsx'
        else:
            new_name = f'{self.klant_code}_{product}_{self.huidige_omgeving[0]}.xlsx'
        return new_name
    
    def update_bestand_locatie(self, new_path):        
        attr = f'excel_{self.huidige_omgeving[0]}'
        setattr(self, attr, new_path)
        return None

    def nieuwe_bevinding(self, indicator, column, bevinding, a = '', p = ''):
        new_row = {'Indicator': indicator, 'Kolom': column, 'A': a, 'P': p, 'Bevinding': bevinding}
        self.bevindingen = concat([self.bevindingen, DataFrame(new_row, index = [0])], ignore_index = True)
        return None

class ZKH(Instelling):

    def __init__(self, klant_code: str):
        super().__init__(klant_code)

        #self.link_dict = HardCodedParameters.zkh_dict

        #self.update_baselink()
        return None


class GGZ(Instelling):

    def __init__(self, klant_code: str):
        super().__init__(klant_code)

        #self.link_dict = HardCodedParameters.ggz_dict

        #self.update_baselink()
        return None