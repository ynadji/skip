#!/usr/bin/env python

import sys
from optparse import OptionParser
from collections import defaultdict
import itertools

from nltk import word_tokenize
from nltk.util import ngrams

def loadraw(path):
    with open(path) as f:
        return f.read().lower()

def tokenize_many(paths):
    raws = []
    for path in paths:
        raws.append(loadraw(path))

    return '\n'.join(raws)

def tokenize(paths):
    return word_tokenize(tokenize_many(paths))

def remove_stopwords(tokens, stopwords):
    return [token for token in tokens if token not in stopwords]

def _build_stopword_list(stopword_list_path):
    with open(stopword_list_path) as f:
        return {x.strip().lower() for x in f}

def ubtgrams(tokens):
    grams = defaultdict(itertools.count().next)

    for n in [1, 2, 3]:
        for ngram in ngrams(tokens, n):
            _ = grams[ngram]

    return grams

def _aggregate_words_by_category(tokens, words, category):
    pass

def _save_part_one(grams, outpath):
    with open(outpath, 'w') as out:
        out.write('label\twords\n')
        for gram, uid in grams.iteritems():
            out.write('%d\t%s\n' % (uid, ' '.join(gram)))

    return 

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] input"
    parser = OptionParser(usage=usage)
    parser.add_option('-s', '--stopword-list', default='data/stopwords.txt',
                      help='Stopword list to use (one word per line; only lowercase)')
    parser.add_option('--food-word-list', default='data/foodwords.txt',
                      help='Food word list to use (one word per line; only lowercase)')
    parser.add_option('-f', '--use-food-words', default=False, action='store_true',
                      help='Use food word list')

    (options, args) = parser.parse_args()

    if len(args) < 0:
        parser.print_help()
        return 2


    # do stuff
    stopwords = _build_stopword_list(options.stopword_list)
    tokens = remove_stopwords(tokenize(args), stopwords)
    grams = ubtgrams(tokens)

    _save_part_one(grams, 'part1.tsv')

if __name__ == '__main__':
    sys.exit(main())
