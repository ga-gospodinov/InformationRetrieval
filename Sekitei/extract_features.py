# coding: utf-8

import sys
from collections import Counter
import urlparse
import urllib
import random
import re

def get_random_urls(file_name, count):
    urls = []
    with open(file_name) as fin:
        for url in fin:
            urls.append(url.strip())
    random.shuffle(urls)
    return urls[:count]

def add_features(features, urls):
    for url in urls:
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

def extract_features(INPUT_FILE_1, INPUT_FILE_2, OUTPUT_FILE):
    features = Counter()
    
    N = 1000
    threshold = 0.1
    min_frequency = N * threshold
    
    add_features(features, get_random_urls(INPUT_FILE_1, N))
    add_features(features, get_random_urls(INPUT_FILE_2, N))
    
    with open(OUTPUT_FILE, "w") as fout:
        for feature in features.most_common():
            if feature[1] > min_frequency:
                fout.write('{feature}\t{count}\n'.format(feature=feature[0], count=feature[1]))