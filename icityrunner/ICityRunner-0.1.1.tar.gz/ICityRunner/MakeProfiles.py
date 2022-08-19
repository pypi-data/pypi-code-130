import argparse
import subprocess
import os
import time
from multiprocessing import Pool

ap = argparse.ArgumentParser(description = "Creates protein profiles in specified folder for clusters in given file")
ap.add_argument("-f", help = "Clusters file name", required = True)
ap.add_argument("-c", help = "Folder name where profiles will be saved", required = True)
ap.add_argument("-d", help = "Path to protein database", required = True)

opts = ap.parse_args()
ClustersFileName = opts.f
ClustersFolderName = opts.c
Database = opts.d

ClusterNo = 0
TmpIDsFileName = "Tmp_IDs.lst"
TmpFASTAFileName = "Tmp_FASTA.faa"

if not os.path.exists(ClustersFolderName):
    subprocess.call("mkdir " + ClustersFolderName, shell = True)

def profile_worker(ClusterNo, Line, Length):
    global ClustersFileName
    print("Processing No: ",'[', ClusterNo, '/', Length,']', "Sequence: ", Line)
    ClusterIDs = Line[:-1].split("\t")[1].split(" ")
    ClusterProfileFileName = "CLUSTER_" + str(ClusterNo) + ".ali"

    with open(TmpIDsFileName, "w") as IDsFile:
        IDsFile.write("\n".join(ClusterIDs))

    subprocess.call("blastdbcmd -db " + Database + " -entry_batch " + TmpIDsFileName + " -long_seqids > " + TmpFASTAFileName,
                    shell=True)

    subprocess.call("muscle -align " + TmpFASTAFileName + " -output " + ClustersFolderName + "/" + ClusterProfileFileName
                    , shell=True)


def multi_process():
    cpu_cnt = os.cpu_count()
    print("CPU Core Num: ", cpu_cnt)
    pool = Pool(cpu_cnt)  # Creating Process Pool
    with open(ClustersFileName, 'r') as File:
        Lines = File.readlines(); Length = len(Lines)
        for ClusterNo, Line in enumerate(Lines):
            print("No.", ClusterNo, "Processing sequence: ", Line)
            pool.apply_async(profile_worker, (ClusterNo + 1, Line, Length))  # Non-Blocking

    pool.close()  # Close Proces Pool Entry
    pool.join()  # Waiting
    print("Work Done !")


if __name__ == '__main__':
    t1 = time.time()
    cnt = 0
    multi_process()

    t2 = time.time()

    subprocess.call("rm " + TmpIDsFileName, shell=True)
    subprocess.call("rm " + TmpFASTAFileName, shell=True)

    print("Used time: ", t2 - t1, "s")




