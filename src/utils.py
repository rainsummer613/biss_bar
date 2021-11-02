import requests
import gzip
from Bio import SeqIO
import os
import logging

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

def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))

