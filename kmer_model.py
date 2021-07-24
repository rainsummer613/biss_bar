from collections import Counter
from utils import *

class Bacteria:
    
    def __init__(self, name, url_prot, url_gen):
        '''
        initialize instance for Species
        
        name: species name
        url_prot: link to download proteom
        url_gen: link to download genome
        '''
        self.name = name
        self.gen_dict = upload(url_gen)
        self.prot_dict = upload(url_prot)
        
    @staticmethod
    def get_kmers(fasta_dict, size, step):
        '''
        get k-mers from raw sequences
        
        fasta_dict: dictionary with raw sequences of a genome/proteome
        size: k (k-mer length)
        step: step size for building k-mer
        
        returns
        kmers: dict of kmers
        kmers_counter: kmers frequencies
        '''
    
        def kmers(sequence, size, step):
            for x in range(0, len(sequence) - size, step):
                yield sequence[x:x+size]
    
        kmers = {k: list(kmers(fasta_dict[k], size, step)) for k in fasta_dict}
        kmers['all'] = sum(list(kmers.values()), [])
        kmers_counter = {k: Counter(v) for k,v in kmers.items()}
        return kmers, kmers_counter
    
    def get_kmers_gen(self, kmer_len=35, kmer_step=1):
        '''
        get and save k-mers for genome to arguments
        
        kmer_len: k (k-mer length)
        kmer_step: step size for building k-mer
        '''
        self.kmers_gen, self.kmers_gen_counter = Bacteria.get_kmers(self.gen_dict, size=kmer_len, step=kmer_step)
    
    def get_kmers_prot(self, kmer_len=5, kmer_step=1):
        '''
        get and save k-mers for proteome to arguments
        
        kmer_len: k (k-mer length)
        kmer_step: step size for building k-mer
        '''        
        self.kmers_prot, self.kmers_prot_counter = Bacteria.get_kmers(self.prot_dict, size=kmer_len, step=kmer_step)
        