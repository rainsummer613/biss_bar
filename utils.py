import requests
import gzip
from Bio import SeqIO

def download(url):
    filename = url.split('/')[-1]
    with open(filename, 'wb') as f:
        r = requests.get(url)
        f.write(r.content)
    return filename

def upload(url):
    filename = download(url)
    with gzip.open(filename, 'rt') as handle:
        return {rec.id: str(rec.seq) for rec in SeqIO.parse(handle, 'fasta')}
    
#def load_prot(url_prot):
#    filename_prot = download(url_prot)
#    return {rec.id.split('|')[1]: str(rec.seq) for rec in SeqIO.parse(filename_prot, 'fasta')}