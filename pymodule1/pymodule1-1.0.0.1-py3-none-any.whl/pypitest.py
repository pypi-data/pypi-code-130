import sys
import re
import os
import time

stGroup = sys.argv[1]
stCDS = sys.argv[2]
stOutDir = sys.argv[3]

stName, stSeq, nGene = "", "", 0
stGroupInfo, stGroupData, stTemp, stTemp2 = [], [], [], ""
hashSeq = {}

# CDS file open
f = open(stCDS, 'r')

while True:
    line = f.readline()
    if not line: break
    line = line.strip()

    if re.search('^>([^\s]+)', line) is not None:
        if stSeq != "":
            hashSeq[stName] = stSeq
            stSeq = ""
        split_name = re.split('^>([^\s]+)', line)
        stName = split_name[1]
    else:
        stSeq = stSeq + line

f.close()
hashSeq[stName] = stSeq

# GroupInfo file open
f = open(stGroup, 'r')
lines = f.readlines()
for line in lines:
    line = line.strip()
    stGroupInfo.append(line)
f.close()

# sort
#stGroupInfo.sort(key=lambda l: re.sub("^([^\t]+)[\t]+", "", l))
stGroupInfo.sort(key=lambda i: (re.search('^([^\t]+)[\t]+', i).group(1), re.search('^[^\t]+[\t]+([^\t]+)[\t]+', i).group(1)))

# temp?
for i in range(len(stGroupInfo)):
    stInfo = re.split('[\t]+', stGroupInfo[i])
    stInfo2 = re.split('[\t]+', stGroupInfo[i + 1])
    if stInfo[0] == stInfo2[0] and stInfo[1] == stInfo2[1]:
        stTemp.append(stInfo[2])
    else:
        stTemp.append(stInfo[2])
        stTemp2 = ",".join(stTemp)
        nTemp = len(stTemp)
        stTemp2 = "{},{}_{},{}".format(nTemp, stInfo[0], stInfo[1], stTemp)
        stGroupData.append(stTemp2)
        stTemp = []

#
for i in range(len(stGroupData)):
    stInfo = stGroupData[i].split(',')
    stPrefix = ""
    nCnt = 0
    arTempData = []
    ks = open(stInfo[1] + ".KS", 'w')
    totalInfo = open(stInfo[1] + ".Kaks", "w")

    for j in range(2, len(stInfo)):
        for k in range(j + 1, len(stInfo)):
            stPrefix = "{}.{},{}".format(stInfo[1], j, k)
            if nCnt == 0:
                nGene = j
            out = open(stPrefix + ".CDS.fasta", 'w')
            out.write(">{}\n{}\n>{}\n{}\n".format(stInfo[j], stSeq[stInfo[j]], stInfo[k], stSeq[stInfo[k]]))
            out.close()

            os.system("/home/programs/prank-re/prank/bin/prank -d=$stPrefix.CDS.fasta -f=fasta -codon -o=$stPrefix")
            time.sleep(10)
            os.system("perl parseFastaIntoAXT.pl $stPrefix.best.fas")
            os.system(
                "/home/programs/KaKs_Calculator2.0/src/KaKs_Calculator -i {}.best.fas.axt -o {}.kaks -m MYN".format(
                    stPrefix, stPrefix))
            nGene1 = j - nGene + 1
            nGene2 = k - nGene + 1

            data = open(stPrefix + ".kaks", "r")
            lines = data.readlines()
            for line in lines:
                line = line.strip()
                if 'Method' in line:
                    continue
                stInfo = re.split('[\s\t]+', line)
                totalInfo.write(line + '\n')

                if stInfo[3] == "NA":
                    stInfo[3] = 0
                elif re.search('[0-9]', stInfo[3]) is None:
                    stInfo[3] = 100

                stTempData = str(nGene1) + "\t" + str(nGene2) + " " + str(stInfo[3]) + "\t" + str(stInfo[0])
                arTempData.append(stTempData)
            data.close()

            nCnt += 1

    # arTempData sort
    arTempData.sort()

    for k in range(len(arTempData)):
        ks.write(arTempData[k])
    ks.close()

    os.system("mv tmpdirprankms* $stOutDir/temp")

    nFilesize = os.system()
    if nFilesize < 1:
        os.system("rm -rf $stOutDir/$stInfo[1].KS")
    if nFilesize > 0:
        os.system("perl MakeRDistFormat.pl $stOutDir/$stInfo[1].KS > $stOutDir/$stInfo[1].matrix")
