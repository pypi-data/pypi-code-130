import pickle
import pandas as pd

class AddInfo(object):
    def __init__(self, config) -> None:
        self.samples = config['samples']
        self.config = config
    
    def run(self):
        if not self.config['skip_samples']:
            df_samp = pd.read_csv(self.config['temp_folder']+'/samples.csv')
        if not self.config['skip_library']:
            df_lib = pd.read_csv(self.config['temp_folder']+'/library.csv').astype({'name':str}).set_index('name')
        for s in self.samples:
            print(s)
            self.config['add_info'] = self.config['add_info']+'/' if self.config['add_info'][-1]!= '/' else self.config['add_info']
            pf = pickle.load(open(self.config['add_info'] + s +'.p', 'rb'))

            for name, mh in pf.items():
                if not self.config['skip_samples']:
                    for col in df_samp.columns:
                        assert not (data:=df_samp[col].loc[df_samp['sample']==s]).empty, f"{s} doesn't have {col} in samples.csv"
                        setattr(mh,col,data)
                if not self.config['skip_library']:
                    for col in df_lib.columns:
                        try:
                            data =df_lib[col].loc[name]
                        except:
                            print( f"{name} not found in library.csv for col {col}")
                        setattr(mh,col,data)
            pickle.dump(pf, open(self.config['add_info'] + s +'.p', 'wb'))
