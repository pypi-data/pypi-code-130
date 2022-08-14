import os

def generate_mh_only_folder(samples):
    if not os.path.exists('output_mh_only'):
        os.mkdir('output_mh_only')
    for s in samples:
        os.system(f"cp output/{s}/BitVector_Files/mh.p output_mh_only/{s}.p")
        print(f"mh_only/{s}.p written")