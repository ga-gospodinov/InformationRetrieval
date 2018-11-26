#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import string
import mmh3
import docreader
import sys
import numpy as np
from collections import defaultdict

class TextNormalizer:
    @staticmethod
    def join_numbers(text):
        regex = re.compile('([\d])[\s]+([\d])')
        return regex.sub('\\1\\2', text)

    @staticmethod
    def clean_out_punct(text):
        regex = re.compile('[%s]' % re.escape(string.punctuation + "«" + "»"))
        return regex.sub(' ', text)

    @staticmethod
    def lower_case(text):
        return text.lower()

    @staticmethod
    def remove_entities(text):
        regex = re.compile('&[0-9a-z_A-Z]+;')
        return regex.sub(' ', text)

    @staticmethod
    def normalize(text):
        return TextNormalizer.lower_case(TextNormalizer.clean_out_punct(TextNormalizer.remove_entities(TextNormalizer.join_numbers(text))))


class MinshinglesCounter:
    SPLIT_RGX = re.compile(r'\w+', re.U)

    def __init__(self, window=5, n=20):
        self.window = window
        self.n = n

    def count(self, text):
        words = MinshinglesCounter._extract_words(text)
        shingles = self._count_shingles(words)
        minshingles = self._select_minshingles(shingles)

        return minshingles

    def _get_order_function(self, num):
        basis = [1663, 1999, 2203, 2381, 2411,
                 2657, 2789, 2843, 2861, 2909,
                 2953, 3169, 3217, 3259, 3491,
                 3467, 3469, 3499, 3511, 27644437]
        return lambda x: divmod(x, basis[num])[1]

    def _select_minshingles(self, shingles):
        minshingle = [None]*self.n

        for shingle in shingles:
            for i in range(self.n):
                hash_i = self._get_order_function(i)
                if minshingle[i] is None or hash_i(shingle) < hash_i(minshingle[i]):
                    minshingle[i] = shingle
        return minshingle

    def _count_shingles(self, words):
        shingles = []
        for i in xrange(len(words) - self.window):
            h = mmh3.hash(' '.join(words[i:i+self.window]).encode('utf-8'))
            shingles.append(h)
        return shingles

    @staticmethod
    def _extract_words(text):
        words = re.findall(MinshinglesCounter.SPLIT_RGX, text)
        return words

def main():
    minshingles_count = 20

    files = sys.argv[1:]
    docs = docreader.DocumentStreamReader(files)
    minshingles_counter = MinshinglesCounter(window=5, n=minshingles_count)

    minshingle2urls = defaultdict(list)
    id2url = []

    url_index = 0
    for doc in docs:
        minshingles = minshingles_counter.count(TextNormalizer.normalize(doc.text))
        if None not in minshingles:
            id2url.append(doc.url)
            for minshingle_id, minshingle in enumerate(minshingles):
                minshingle2urls[(minshingle_id, minshingle)].append(url_index)
            url_index += 1

    urls_matrix = np.zeros((len(id2url), len(id2url)))

    for minshingle, url_ids in minshingle2urls.iteritems():
        count = 0
        for id_i in url_ids:
            count += 1
            for id_j in url_ids[count:]:
                urls_matrix[id_i, id_j] += 1

    count = 0
    for id_i in range(len(id2url)):
        count += 1
        for id_j in range(count, len(id2url)):
            if id_j > id_i:
                measure = float(urls_matrix[id_i, id_j]) / minshingles_count
                if measure > 0.75:
                    print id2url[id_i], id2url[id_j], measure

if __name__ == '__main__':
    main()
