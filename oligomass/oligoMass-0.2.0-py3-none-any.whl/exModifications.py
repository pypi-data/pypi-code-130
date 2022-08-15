import pandas as pd


class exModifDB():
    def __init__(self):
        self.data = None

    def get_mod_properties(self, mod_code):
        pass

class exModifDataFrame(exModifDB):
    def __init__(self):
        super().__init__()

        self.data = {'code': [], 'mass': [], 'ext_cf': [], 'formula+': [], 'formula-': []}

        self.data['code'].append('5Phos')
        self.data['mass'].append(80.)
        self.data['ext_cf'].append(0)
        self.data['formula+'].append('')
        self.data['formula-'].append('')

        self.data['code'].append('iFluorT')
        self.data['mass'].append(816.7)
        self.data['ext_cf'].append(13700)
        self.data['formula+'].append('')
        self.data['formula-'].append('')

        self.data['code'].append('+m')
        self.data['mass'].append(0)
        self.data['ext_cf'].append(0)
        self.data['formula+'].append('C2H2O')
        self.data['formula-'].append('')

        self.data['code'].append('LNA')
        self.data['mass'].append(0)
        self.data['ext_cf'].append(0)
        self.data['formula+'].append('CO')
        self.data['formula-'].append('')

        self.data['code'].append('tio')
        self.data['mass'].append(0)
        self.data['ext_cf'].append(0)
        self.data['formula+'].append('S')
        self.data['formula-'].append('O')

        self.data['code'].append('6FAM')
        self.data['mass'].append(537.5)
        self.data['ext_cf'].append(20960)
        self.data['formula+'].append('')
        self.data['formula-'].append('')

        self.data['code'].append('56-FAM')
        self.data['mass'].append(537.5)
        self.data['ext_cf'].append(20960)
        self.data['formula+'].append('')
        self.data['formula-'].append('')

        self.data['code'].append('xFAM')
        self.data['mass'].append(537.5)
        self.data['ext_cf'].append(20960)
        self.data['formula+'].append('')
        self.data['formula-'].append('HPO2')

        #C36O8NH40

        self.data['code'].append('SIMA')
        self.data['mass'].append(759)
        self.data['ext_cf'].append(31600)
        self.data['formula+'].append('')
        self.data['formula-'].append('')

        self.data['code'].append('xSIMA')
        self.data['mass'].append(759)
        self.data['ext_cf'].append(31600)
        self.data['formula+'].append('')
        self.data['formula-'].append('HPO2')

        self.data['code'].append('BHQ1')
        self.data['mass'].append(0)
        self.data['ext_cf'].append(35935)
        self.data['formula+'].append('C21H18N6O3C4O2H9PO2')
        self.data['formula-'].append('')

        self.data['code'].append('3BHQ_1')
        self.data['mass'].append(0)
        self.data['ext_cf'].append(35935)
        self.data['formula+'].append('C21H18N6O3C4O2H9PO2')
        self.data['formula-'].append('')

        self.data['code'].append('BHQ2')
        self.data['mass'].append(0)
        self.data['ext_cf'].append(34000)
        self.data['formula+'].append('C20H16N6O4C4O2H9PO2')
        self.data['formula-'].append('')

        self.data['code'].append('Cy5')
        self.data['mass'].append(612)
        self.data['ext_cf'].append(250000)
        self.data['formula+'].append('')
        self.data['formula-'].append('')

        self.data['code'].append('xCy5')
        self.data['mass'].append(612)
        self.data['ext_cf'].append(250000)
        self.data['formula+'].append('')
        self.data['formula-'].append('HPO2')

        self.data['code'].append('Cy5.5')
        self.data['mass'].append(712)
        self.data['ext_cf'].append(198000)
        self.data['formula+'].append('')
        self.data['formula-'].append('')

        self.data['code'].append('xCy5.5')
        self.data['mass'].append(712)
        self.data['ext_cf'].append(198000)
        self.data['formula+'].append('')
        self.data['formula-'].append('HPO2')

        self.data = pd.DataFrame(self.data)
        self.data = self.data.set_index('code')

        self.data['in_base'] = [True for i in self.data['mass']]

        #df = self.data.reset_index()
        #df.to_csv('external_mods.csv', sep='\t', index=False)
        self.read_external_mods_from_csv()

    def get_mod_properties(self, mod_code):
        if mod_code in self.data.index:
            return self.data.loc[mod_code].to_dict()
        else:
            return {'mass': 0, 'ext_cf': 0, 'formula+': '', 'formula-': '', 'in_base': False}

    def read_external_mods_from_csv(self, fname='external_mods.csv'):
        df = pd.read_csv(fname, sep='\t')
        df.fillna('', inplace=True)
        self.data = df.set_index('code')



def test():
    db = exModifDataFrame()
    print(db.data.loc['5Phos'].to_dict())
    print(db.get_mod_properties('5Phos'))

def test2():
    db = exModifDataFrame()
    df = db.data
    df.reset_index(inplace=True)
    df.to_csv('external_mods.csv', index=False, sep='\t')
    print(df)

def test3():
    db = exModifDataFrame()
    db.read_external_mods_from_csv()
    print(db.data)

if __name__ == '__main__':
    test3()