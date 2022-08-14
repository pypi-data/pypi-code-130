
import pandas as pd
import os
import yaml
from dreem_herschlag.util import Path, run_command


class Sanity_check(object):
    def __init__(self, config) -> None:
        self.samples = config['samples']
        self.path_to_data = config['path_to_data'] if config['path_to_data'][-1] == '/' else config['path_to_data'] + '/'
        self.sample_file = self.path_to_data+'samples.csv'
        self.library_file = self.path_to_data+'library.csv'
        self.dreem_args = config['dreem_args']
        self.verbose = config['verbose']
        self.fastq_zipped = config['fastq_zipped']
        self.path = Path()
        self.config = config

    def files(self):
        # check that every file is there
        if self.config['run_dreem']:
            assert len(fasta :=self.find_fasta()) > 0, "No fasta found"
            print('Found fasta_file '+fasta)
            for s in self.samples:
                for f in [x + '.gz' if self.fastq_zipped else x for x in ['_R1_001.fastq', '_R2_001.fastq']]:
                    assert os.path.exists(self.path_to_data+s+f), f"{self.path_to_data+s+f} not found"
        if self.config['add_info']:
            for s in self.samples:
                assert os.path.exists(self.path_to_data+s+'.p'), f"{self.path_to_data+s+'.p'} not found"
        if not self.config['skip_library']:
            assert os.path.exists(self.library_file), f"{self.library_file} not found"        
        if not self.config['skip_samples']:
            assert os.path.exists(self.sample_file), f"{self.sample_file} not found"


    def find_fasta(self):
        cmd = 'find '+self.path_to_data+' -name "*.fasta" -type f'
        output, error_msg = run_command(cmd)
        if error_msg:
            print(error_msg)
            return None
        else:
            assert len(output[:-1].split('\n')) < 2, 'Found more than one fasta file'
            return output.split('\n')[0].replace('//','/')

    def check_samples(self):
        if self.verbose: print(f"Checking {self.sample_file}")
        # check the sanity of samples.csv
        df = pd.read_csv(self.sample_file)
        assert len(df['sample']) == len(df['sample'].unique()), "Every line isn't unique in samples.csv"

        # check that every sample as a corresponding line of samples.csv
        for s in self.samples:
            assert s in list(df['sample']), f"{s} doesn't have a corresponding line in samples.csv"

        with open(self.path.sample_attribute_path, 'r') as f:
            sample_attributes = yaml.safe_load(f)

        assert len(df['exp_env'].unique()) == 1, "exp_env is not unique in samples.csv"
        exp_env = df['exp_env'].unique()[0]

        # check that every column of samples.csv is in sample_attributes.yml
        assert exp_env in ['in_vivo','in_vitro'], f"{exp_env} is not a valid value for exp_env. Should be in_vivo or in_vitro"
        # Check that you have all mandatory columns
        for mand in sample_attributes['mandatory']['all'] + sample_attributes['mandatory'][exp_env]:
            assert mand in list(df.columns), f"{mand} is not in samples.csv"
        
        # check that every mandatory column of samples.csv is not empty for every sample
        for mand in sample_attributes['mandatory']['all'] + sample_attributes['mandatory'][exp_env]:
            for s in self.samples:
                assert df[df['sample']==s][mand].isnull().sum() == 0, f"{mand} is empty in samples.csv for sample {s}"
            
        # Drop unauthorised columns
        for col in list(df.columns):
            if col not in sample_attributes['mandatory']['all'] + sample_attributes['mandatory'][exp_env] \
                + sample_attributes['optional']['all'] + sample_attributes['optional'][exp_env]:
                if col in sample_attributes['optional']: 
                    if self.verbose: print(f"Ignored {col}, not in sample_attributes")
                    df = df.drop(columns=col)

        df.to_csv(self.config['temp_folder']+'/samples.csv', index=False)
        if self.verbose: print('Checking samples.csv done\n')
        return 1

    def check_library(self):
        # check the sanity of libraries.csv
        if self.verbose: print(f"Checking library.csv")
        df = pd.read_csv(self.library_file)
        assert 'name' in list(df.columns), "name is not in library.csv"
        assert len(df['name']) == len(df['name'].unique()), f"Every name isn't unique in library.csv"
        with open(self.path.library_attributes_path, 'r') as f:
            library_attributes = yaml.safe_load(f)
        # check that every mandatory column is there
        for mand in library_attributes['mandatory']:
            assert mand in list(df.columns), f"{mand} is not in library.csv"
            # check that every mandatory column of samples.csv is not empty for every sample
            assert df[df['name'] != ''][mand].isnull().sum() == 0, f"{mand} is empty for at a least one row in library.csv"
            
        
        # check that every column of libraries.csv is in resources/library_attributes.yml
        for col in list(df.columns):
            if col not in library_attributes['mandatory'] + library_attributes['optional']:
                if self.verbose: print(f"Ignored {col}, not in library_attributes")
                df = df.drop(columns=col)
        if not os.path.exists( self.config['temp_folder']):
            os.makedirs( self.config['temp_folder'])
        df.to_csv(f"{self.config['temp_folder']}/library.csv", index=False)

        if self.verbose: print(f"Checking library.csv done\n")

    def run(self):
        if self.verbose: print("Checking files")
        self.files()
        if not self.config['skip_library']:
            self.check_library()
        if not self.config['skip_samples']:
            self.check_samples()
        if self.verbose: print("Checking files done\n")
        return 1