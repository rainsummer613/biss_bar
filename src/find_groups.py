import os
import pickle
import json
import pandas as pd
import numpy as np
import multiprocessing as mp

def count_kmer(kmer, output, i):
    kmer_count = {'H-': [], 'H+': []}
    for gr in bact_groups:
        print('PROC', i, gr)
        for bact in bact_groups[gr]:
            bact_path = kmer_dir + bact + '.csv'

            print('PROC', i, bact_path)
            if os.path.isfile(bact_path):
                df_cur = pd.read_csv(bact_path)

                if kmer in df_cur['kmer'].tolist():
                    count = df_cur.loc[df_cur['kmer']==kmer]['count'].values[0]
                    print('PROC', i, count, '\n')
                    #bact_groups_count[kmer][gr].append((bact, count))
                    kmer_count[gr].append((bact, count))
    output[kmer] = kmer_count

df = pd.read_csv('biss.csv')
kmers = {'cgtcagctcgtgtcgtgagatgttgggttaagtcc': 0.1447389930252834, 'cgtatcggaaggtgcggctggatcacctcctttct': 0.08164251207729471, 'gggttcagaacgtcgtgagacagttcggtccctat': 0.06966920089450013, 'acgtattaccgcggctgctggcacgtagttagccg': 0.0524294198880686, 'ctacgtattaccgcggctgctggcacgtagttagc': 0.04399539262820513, 'agggaccgaactgtctcacgacgttctgaacccag': 0.0433690200617284, 'gatagggaccgaactgtctcacgacgttctgaacc': 0.037986323016564974, 'ttgcgggacttaacccaacatctcacgacacgagc': 0.03218384185517805, 'CTTGTGCGGGCCCCCGTCAATTCCTTTGAGTTTCA': 0.02570000774023763, 'tgtcgggtaagttccgacccgcacgaaaggcgtaa': 0.02370861220690572}
kmers = {k.upper():v for k,v in kmers.items()}
kmer_dir = 'res/kmer_gen/31/'    
    
df = df.replace('H=', 'H+')
groups = df.groupby('group')
bact_groups = {}
for gr,d in groups:
    bact_groups[gr] = d.bact.tolist()
bact_groups_count = {kmer:{'H+':[], 'H-':[]} for kmer in kmers}

output = mp.Manager()
output = output.dict()
processes = []

for i,kmer in enumerate(kmers):
    p = mp.Process(target=count_kmer, args=(kmer, output, i))
    processes.append(p)
    print(f'{p.name} started')
    p.start()

for p in processes:
    p.join()

'''
results = []
while not output.empty():
    o = output.get()
    results.append(o)
bact_groups_count = dict(zip(kmers.keys(), results))
'''

bact_groups_count = dict(output)
bact_groups_count = {k: (v, bact_groups_count[k]) for k,v in kmers.items()}

with open('res/bact_groups_count1.pkl', 'wb') as bact_file:
    pickle.dump(bact_groups_count, bact_file)
print(bact_groups_count)