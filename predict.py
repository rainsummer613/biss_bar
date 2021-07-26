import pickle
import argparse
from ome import Genome
from utils import *

model_path = 'res/models/rf11_kmer31.pkl'
vectorizer_path = 'res/vectors/kmer31_plus_tfidf_vectorizer.pkl'
labels= ['непатогенная', 'патогенная']
error_msg = 'Что-то пошло не так. Пожалуйста, проверьте корректность ссылки или попробуйте загрузить другую!'

def load_models(model_path, vectorizer_path):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    return model, vectorizer

def get_args():
    parser = argparse.ArgumentParser("Модель для определения потенциальной патогенности бактерий")
    parser.add_argument("-n", "--name", type=str, default='Clostridium asparagiforme', help='название бактерии')
    parser.add_argument("-u", "--url", type=str, default='https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/003/466/005/GCF_003466005.1_ASM346600v1/GCF_003466005.1_ASM346600v1_genomic.fna.gz', help='ссылка на скачивание архива с геномом в формате .fasta.gz')
    args = parser.parse_args()
    return args    
   
if __name__ == '__main__':
    opt = get_args()
    print('models loading')
    model, vectorizer = load_models(model_path, vectorizer_path)
    print('models loaded')    

    try:
        print('genome downloading')
        genome = Genome(opt.name, opt.url)
        print('calculating kmers')
        genome.get_kmers()
        print('vectorizing')
        vector = vectorizer.transform([' '.join(genome.kmers['all'])])
        print('vectorized')
        pred = model.predict(vector)  
        print('predicted!') 
        res = labels[pred[0]]
    except:
        res = error_msg
    print(res)
