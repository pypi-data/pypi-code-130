import time

t1 = time.time()

def do_nothing():
    x = 10
    y = 9
    z = x - y
    return z

for i in range(1000000000):
    do_nothing()

print(time.time() - t1, " seconds")

exit()








import apalib.config as config
import json
import apalib

data = apalib.Data()

# with open(r"apalib/data/chemistry.json", "w") as f:
#     json.dump(data.GetJson(), f, indent=3)


pdb = apalib.PDB()
# pdb.Fetch('5u59') #Solid protein
# pdb.Fetch('4kpy') #DNA-containing protein
# pdb.Fetch('3wbm') #RNA-containing protein
# pdb.WritePDB('testpdb.pdb')
# pdb.RemoveWater()
# pdb.WritePDB()
# pdb.Contents().DumpAtoms()
pdb.Read(r"C:\Users\natem\OneDrive\Desktop\Research\ccSASA - Copy\1j1j\1j1j.mmol")
(apalib.GetUnfoldedSASA(pdb.Contents().GetPeptideChains()['A']))

pdb.RemoveWater()

(pdb.Contents().GetPeptideChains()['A'][1].GetAtoms()[0].GetRadius())
(pdb.Contents().GetPeptideChains()['A'][1].GetAtoms()[0].GetConfiguration(extended = True))
# print(pdb.Contents().DumpAtoms())

one = pdb.Contents().GetPeptideChains()['A'][1]
two = pdb.Contents().GetPeptideChains()['A'][2]

val = apalib.VectorPair(one, two)
(val)

(apalib.GetCentAngle(one, two, rad=False))

data = apalib.Data()
pdb.Read(r"C:\Users\natem\OneDrive\Desktop\Research\ccSASA - Copy\1j1j\1j1j.mmol")
("Stop")
