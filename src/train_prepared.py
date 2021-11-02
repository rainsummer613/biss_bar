import pandas as pd
import random
import pickle
import os
import numpy as np
import pandas as pd
import pickle
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import f1_score
from ome import Genome, Proteome, Ome
from utils import *

logger0 = setup_logger('logger_base', f'logs/kmer_train_prep.log')
logger0.debug('logging started')

kmer_len = 31
tfidf_name = f'res/vectors/kmer{kmer_len}_plus_tfidf.pickle'
vectorizer_name = f'res/vectors/kmer{kmer_len}_plus_tfidf_vectorizer.pickle'

if os.path.isfile(tfidf_name):
    with open(tfidf_name, 'rb') as vect_file:
        X_train = pickle.load(vect_file)

if os.path.isfile(vectorizer_name):
    with open(vectorizer_name, 'rb') as vect_file:
        vectorizer = pickle.load(vect_file)

features = vectorizer.get_feature_names()
logger0.info(f'feature names {features}')

df = pd.read_csv('biss1.csv', encoding='utf-8')
y_train = df['group'].values
logger0.info(f'y_train {y_train}')

logger0.info(f'training size X {X_train.shape} y {len(y_train)}')
methods = (RandomForestClassifier(n_estimators=4),
               RandomForestClassifier(n_estimators=5),
               RandomForestClassifier(n_estimators=6),
               RandomForestClassifier(n_estimators=7),
               RandomForestClassifier(n_estimators=8),
               RandomForestClassifier(n_estimators=10),
               RandomForestClassifier(n_estimators=11),
               RandomForestClassifier(n_estimators=12),
               RandomForestClassifier(n_estimators=13),
               RandomForestClassifier(n_estimators=15),           
               )

for i,method in enumerate(methods):
    f1_cv = cross_val_score(method, X_train, y_train, cv=5, scoring='f1')
    logger0.info(f'method {method}')
    logger0.info(f'f1 cv {f1_cv}, MEAN {np.mean(f1_cv)}')

    clf = method
    clf.fit(X_train, y_train)
    importances = clf.feature_importances_
    importances = {k:v for k,v in enumerate(importances)}
    importances = {k: v for k, v in sorted(importances.items(), reverse=True, key=lambda item: item[1])}
    importances10 = {features[k]: importances[k] for k in list(importances)[:10]}
    logger0.info(f'{importances10}')

    with open(f'res/models/rf{i+4}_kmer{kmer_len}.pkl', 'wb') as vect_file:
        pickle.dump(clf, vect_file) 

y_train = list(y_train)
random.shuffle(y_train)
logger0.info(f'y_train {y_train}')
folds = list(chunks(list(y_train), len(y_train)//5))
f1_base = []
for i,f in enumerate(folds):
    train = sum(folds[:i] + folds[i+1:],[])
    common = Counter(train).most_common(1)[0][0]
    pred = [common for _ in f]
    logger0.info(f'true {f}, pred {pred}')
    f1_base.append(f1_score(f, pred))
logger0.info(f'f1 baseline {f1_base}')