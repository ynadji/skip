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

# TODO: remove digits & punctuation
def remove_stopwords(tokens, stopwords):
    return [token for token in tokens if token not in stopwords]

def _build_stopword_list(stopword_list_path):
    with open(stopword_list_path) as f:
        return {x.strip().lower() for x in f}

def ubtgrams(tokens, word_categories=None):
    grams = defaultdict(itertools.count().next)

    # get single tokens before ngramming
    if word_categories:
        tokens = [word_categories.get((token, ), token) for token in tokens]

    for n in [1, 2, 3]:
        for ngram in ngrams(tokens, n):
            if word_categories:
                ngram = word_categories.get(ngram, ngram)
            _ = grams[ngram]

    return dict(grams)

def _load_categorizer(category_tsv):
    word_categories = {}
    with open(category_tsv) as f:
        _ = f.readline()
        for line in f:
            tokens, category = line.lower().strip().split('\t')
            grams = tuple(tokens.split())
            word_categories[grams] = category

    return word_categories

def _save_part_one(grams, outpath):
    with open(outpath, 'w') as out:
        out.write('label\twords\n')
        for gram, uid in grams.iteritems():
            out.write('%d\t%s\n' % (uid, ' '.join(gram)))

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] input"
    parser = OptionParser(usage=usage)
    parser.add_option('-s', '--stopword-list', default='data/stopwords.txt',
                      help='Stopword list to use (one word per line; only lowercase)')
    parser.add_option('--category-word-list', default='data/category_words.tsv',
                      help='Category word list to use (TAB separated, 1 line header, wordTABcategory)')
    parser.add_option('-c', '--use-categories', default=False, action='store_true',
                      help='Use categories')

    (options, args) = parser.parse_args()

    if len(args) < 0:
        parser.print_help()
        return 2


    # do stuff
    stopwords = _build_stopword_list(options.stopword_list)
    tokens = remove_stopwords(tokenize(args), stopwords)

    if options.use_categories:
        sys.stderr.write('Using category file: %s...\n' % options.category_word_list)
        word_categories = _load_categorizer(options.category_word_list)
        grams = ubtgrams(tokens, word_categories)
    else:
        grams = ubtgrams(tokens)

    _save_part_one(grams, 'part1.tsv')

if __name__ == '__main__':
    sys.exit(main())
