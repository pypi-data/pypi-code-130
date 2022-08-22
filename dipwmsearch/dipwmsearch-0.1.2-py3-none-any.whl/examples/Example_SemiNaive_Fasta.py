#!/usr/bin/env python3
#_*_ coding:utf-8 _*_

# example SemiNaive search with LAM and ratio
# from simple fasta file
import sys
from src.diPwm import diPWM, create_diPwm
from src.SemiNaive import search_semi_naive_LAM_ratio
from Bio import SeqIO
from Bio.Seq import Seq

# create diPWM object from path
diP = create_diPwm(sys.argv[1])

# create object SeqIO from fasta file
file = open(sys.argv[2])
seqRecord = SeqIO.read(file, "fasta")

# convert sequence text in uppercase
mySeq = seqRecord.seq.upper()

# print for each solution : starting position in the sequence, word, score
for i, word, score in search_semi_naive_LAM_ratio(diP, mySeq, float(sys.argv[3])):
	print(f'{i}\t{word}\t{score}')
