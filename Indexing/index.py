# -*- coding: utf-8 -*-

import docreader
import doc2words
from collections import defaultdict
import pickle

args = docreader.parse_command_line().files

compressor_type = args[0]

if compressor_type == 'varbyte':
	import varbyte
	compressor = varbyte
elif compressor_type == 'simple9':
	import simple9
	compressor = simple9

docs = docreader.DocumentStreamReader(args[1:])

doc_id = 1
term2doc = defaultdict(list)
doc_id2url = []
for doc in docs:
	doc_id2url.append(doc.url)
	words = doc2words.extract_words(doc.text)
	unique_words = set(words)
	for word in unique_words:
		key = abs(hash(word.encode('utf-8')))
		term2doc[key].append(doc_id)
	doc_id += 1

for key in term2doc:
	term2doc[key] = compressor.code(term2doc[key])

with open('term2doc.pickle', 'wb') as handle:
	handle.write(compressor_type + '\n')
	pickle.dump(term2doc, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('doc_id2url.pickle', 'wb') as handle:
    pickle.dump(doc_id2url, handle)