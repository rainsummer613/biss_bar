import os
import numpy as np
import pandas as pd
import pickle
from collections import Counter
import multiprocessing as mp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import f1_score
from ome import Genome, Proteome, Ome
from utils import *

kmer_len = 31
logger0 = setup_logger('logger_base', f'logs/kmer_train.log')
logger0.debug('logging started')

if os.path.isfile('biss1.csv'):
    df = pd.read_csv('biss1.csv', encoding='utf-8')
else:
    df = pd.read_csv('biss.csv', encoding='utf-8')
    df.dropna(subset=['gen'], inplace=True)
    df['group'] = df['group'].replace('H=','H+')
    df['group'] = df['group'].replace({'H-':1, 'H+': 0})
    df = df.sample(frac=1)
    df.to_csv('biss1.csv', index=True)
    df.reset_index(drop=True, inplace=True)

#all_gen, all_prot = {}, {}
corpus_gen, corpus_prot = [], []

for i in range(df.shape[0]):
    bact_name = df['bact'][i]
    logger0.info(f"{bact_name}, {df['gen'][i]}, {df['prot'][i]}")
    
    genome = Genome(bact_name, df['gen'][i])
    genome.get_kmers()
    
    #all_gen[bact_name] = genome.seq
    corpus_gen.append(' '.join(genome.kmers['all']))

    df1 = pd.DataFrame.from_dict(genome.kmers_counter)
    df1.reset_index(level=0, inplace=True)
    df1 = df1[['index', 'all']]
    df1.columns = ['kmer', 'count']
    res_filename = f'res/kmer_gen/{kmer_len}/{bact_name}.csv'
    if not os.path.isfile(res_filename):
        df1.to_csv(f'res/kmer_gen/{kmer_len}/{bact_name}.csv', index=False)  
    logger0.info('done')

logger0.info('START vectorization')
y_train = df['group']
logger0.info(f'y counts: {y_train.value_counts()}')
vect_name = f'res/vectors/kmer{kmer_len}_plus_tfidf.pickle'

if not os.path.isfile(vect_name):
    vectorizer = TfidfVectorizer(min_df=.1, max_df=.7, max_features=250)
    X_train = vectorizer.fit_transform(corpus_gen)
    with open(vect_name, 'wb') as vect_file:
        pickle.dump(X_train, vect_file)    
    with open(f'res/vectors/kmer{kmer_len}_plus_tfidf_vectorizer.pickle', 'wb') as vect_file:
        pickle.dump(vectorizer, vect_file)    
    
else:
    with open(vect_name, 'rb') as vect_file:
        X_train = pickle.load(vect_file)

methods = (RandomForestClassifier(n_estimators=5),
               RandomForestClassifier(n_estimators=10),
               RandomForestClassifier(n_estimators=15),
               RandomForestClassifier(n_estimators=30),
               RandomForestClassifier(n_estimators=50),
               MultinomialNB(alpha=0.7),
               MultinomialNB(alpha=1.0),
               LogisticRegression(penalty='l2', class_weight='balanced', C=0.5),
               LogisticRegression(penalty='l2', class_weight='balanced', C=1.0),
               AdaBoostClassifier(n_estimators=5),
               AdaBoostClassifier(n_estimators=10),
               AdaBoostClassifier(n_estimators=30)
               )

logger0.info(f'training size X {X_train.shape} y {len(y_train)}')

cv_num = 5
for method in methods:
    f1_cv = cross_val_score(method, X_train, y_train, cv=cv_num, scoring='f1')
    logger0.info(f'method {method}')
    logger0.info(f'f1_cv {f1_cv}')

y_train = list(y_train)
folds = list(chunks(list(y_train), len(y_train)//cv_num))
f1_base = []
for i,f in enumerate(folds):
    train = sum(folds[:i] + folds[i+1:],[])
    common = Counter(train).most_common(1)[0][0]
    pred = [common for _ in f]
    f1_base.append(f1_score(f, pred))
logger0.info(f'f1 baseline {f1_base}')