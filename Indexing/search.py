# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pickle

if __name__ == "__main__":

	with open('term2doc.pickle', 'rb') as handle:
		compressor_type = handle.readline().strip()
		term2doc = pickle.load(handle)

	if compressor_type == 'varbyte':
		import varbyte
		compressor = varbyte
	elif compressor_type == 'simple9':
		import simple9
		compressor = simple9

	with open('doc_id2url.pickle', 'rb') as handle:
		doc_id2url = pickle.load(handle)

	for line in sys.stdin:
		words = line.strip().decode("utf-8").lower().encode('utf-8').replace(' ', '').split('&')
		keys = []
		for word in words:
			keys.append(abs(hash(word.encode('utf-8'))))

		doc_ids = set(compressor.decode(term2doc[keys[0]]))

		for key in keys[1:]:
			doc_ids = doc_ids.intersection(compressor.decode(term2doc[key]))

		print len(doc_ids)

		for doc_id in sorted(list(doc_ids)):
			print doc_id2url[doc_id - 1]