 # coding: utf-8

import sys
import os
import re
import random
import time
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from collections import Counter
import numpy as np
import urlparse
import urllib

class sekitei:
    pass

def feature_extractor(url):
    features = Counter()
    index = 0
    parsed_url = urlparse.urlparse(url)
    for segment in urllib.unquote(parsed_url.path).split('/'):
        if segment == '':
            continue
        features['segment_name_{index}:{val}'.format(index=index, val=segment)] += 1
        features['segment_len_{index}:{val}'.format(index=index, val=len(segment))] += 1
        if segment.isdigit():
            features['segment_[0-9]_{index}:1'.format(index=index)] += 1
            
        if re.match(r'[^\d]+\d+[^\d]+$', segment):
            features['segment_substr[0-9]_{index}:1'.format(index=index)] += 1
            
        if '.' in segment:
            features['segment_ext_{index}:{ext}'.format(index=index, ext=segment.split('.')[-1])] += 1
                
        if re.match(r'[^\d]+\d+[^\d]+$', segment) and '.' in segment:
            features['segment_ext_substr[0-9]_{index}:{ext}'.format(index=index, ext=segment.split('.')[-1])] += 1
                
        index += 1
            
    features['segments:{count}'.format(count=index)] += 1
        
    if parsed_url.query != '':
        queries = urllib.unquote(parsed_url.query).split('&')
        for query in queries:
            if '=' in query:
                features['param:{keyvalue}'.format(keyvalue=query)] += 1
                features['param_name:{name}'.format(name=query.split('=')[0])] += 1    
            else:
                features['param_name:{name}'.format(name=query)] += 1
    return features
                    
def feature_selector(features, N, threshold=0.1):
    min_frequency = N * threshold
    for key, value in list(features.items()):
        if value < min_frequency:
            del features[key]

def add_features(all_features, feature_names, urls):
    for url in urls:
        features = feature_extractor(url)
        all_features += features
        feature_names.append(features)
    return all_features
        
def get_matrix_representation(url_count, all_features, feature_names):
    X = np.zeros(shape=(url_count, len(all_features)))
    for i in range(url_count):
        for j, key in enumerate(all_features.keys()):
            X[i, j] = feature_names[i][key]
    return X

def define_segments(QLINK_URLS, UNKNOWN_URLS, QUOTA):
    qlinks_count = len(QLINK_URLS)
    ulinks_count = len(UNKNOWN_URLS)
    N_train = qlinks_count + ulinks_count
    all_features = Counter()
    feature_names = []
    all_features = add_features(all_features, feature_names, QLINK_URLS)
    all_features = add_features(all_features, feature_names, UNKNOWN_URLS)
    
    feature_selector(all_features, N_train, threshold=0.05)
    sekitei.all_features = all_features
    X = get_matrix_representation(N_train, all_features, feature_names)
    
    sekitei.qlink_predictor = LogisticRegression()
    sekitei.qlink_predictor.fit(X, np.array([1]*qlinks_count + [0]*ulinks_count))
    
    clusters_count = 10
    sekitei.model = KMeans(n_clusters=clusters_count, init='k-means++')
    predictions = sekitei.model.fit_predict(X)

    clusters = np.empty(clusters_count, dtype='object')
    for i in range(clusters.size):
        clusters[i] = []

    for index, key in enumerate(predictions):
        clusters[key].append(index)

    q_link_ratios = np.zeros(clusters_count)

    for key, value in enumerate(clusters):
        indexes = np.array(value)
        try:
            q_link_ratios[key] = float(indexes[indexes >= qlinks_count].size) / indexes.size
        except:
            q_link_ratios[key] = 0.0
    
    sekitei.q_link_ratios = q_link_ratios
    sekitei.quota_per_cluster = np.round(q_link_ratios / q_link_ratios.sum() * QUOTA)

def fetch_url(url):
    feature_names = []
    add_features(Counter(), feature_names, url)
    x = get_matrix_representation(1, sekitei.all_features, feature_names)
    cluster = sekitei.model.predict(x)
    return random.random() < sekitei.q_link_ratios[cluster] * sekitei.qlink_predictor.predict_proba(x)[0][1]
    '''
    if sekitei.quota_per_cluster[cluster] > 0:
        sekitei.quota_per_cluster[cluster] -= 1
        return False
    else:
        return True
    '''