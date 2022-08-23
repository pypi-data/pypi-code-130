# import Asclepius dependencies
from asclepius.instelling import GGZ, ZKH, Instelling
from asclepius.medewerker import Medewerker

# import other dependencies


class ReleaseTest:
    
    def __init__(self, gebruiker: Medewerker, losse_bestanden: bool = False):

        # Initialiseren
        self.gebruiker = gebruiker

        self.losse_bestanden = losse_bestanden
        
        return None
    
    def test_bi(self, *instellingen: GGZ|Instelling|ZKH):
        from asclepius.regressietest import RegressieTest, TestExcel

        te = TestExcel(join_col = 'Titel', header_row = 0, test_cols = ['Norm', 'Realisatie'])

        # import hardcoded information from fileserver
        import sys
        sys.path.append(r'\\valuecare.local\fileserver\Algemeen\Automatisch testen\Python')
        from parameters import HardCodedParameters as HCP
        var_links = HCP.ggz_variabele_links

        rt = RegressieTest(self.gebruiker, product = 'bi', test_excel = te, variabele_links = var_links)

        rt.test(*instellingen)

        return None
    
    def test_var(self, *instellingen: GGZ|Instelling|ZKH):
        from asclepius.regressietest import RegressieTest, TestExcel

        te = TestExcel(join_col = 'Financier', header_row = 0, test_cols = ['Omzet', 'Omzet norm'])

        # import hardcoded information from fileserver
        import sys
        sys.path.append(r'\\valuecare.local\fileserver\Algemeen\Automatisch testen\Python')
        from parameters import HardCodedParameters as HCP
        T_LINK = HCP.ggz_dict['omzetprog_per_financier']
        D_LINK = HCP.ggz_dict['omzetprog_per_financier_download']

        rt = RegressieTest(self.gebruiker, product = 'var', test_excel = te, target_link = T_LINK, download_link = D_LINK)

        rt.test(*instellingen)

        return None