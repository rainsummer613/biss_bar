import requests
import gzip
from Bio import SeqIO
import os

def download(url):
    '''
    download .bz file from url
    
    url: download link
    '''
    filename = url.split('/')[-1]
    if not os.path.isfile(filename):
        with open(filename, 'wb') as f:
            r = requests.get(url)
            f.write(r.content)
    return filename

def upload(url):
    '''
    upload and parse file from link
    
    url: upload link
    
    return parsed dictionary
    '''
    filename = download(url)
    with gzip.open(filename, 'rt') as handle:
        return {rec.id: str(rec.seq) for rec in SeqIO.parse(handle, 'fasta')}