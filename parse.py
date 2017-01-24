#!/usr/bin/env python

import sys
from optparse import OptionParser
from collections import defaultdict, Counter
import itertools
import string
import os

from nltk import word_tokenize
from nltk.util import ngrams, skipgrams
import xlrd

# TODO:
# * add logging
# * py2exe with drag'n'drop
# * handle skipgram boundaries. this means:
#   * compute skipgram per review, or
#   * compute skipgram per category
# tbh, in practice this won't really matter probably. it will get
# washed out given the size of the data.

def fuckunicode(s):
    def isascii(c): return ord(c) < 128
    return filter(isascii, s)

def tokenfilter(token):
    punctuation = string.punctuation.replace('$', '')
    return str(fuckunicode(token)).translate(None, punctuation)

def loadcells(review_cells):
    try:
        return [tokenfilter(cell.value.lower()) for cell in review_cells]
    except AttributeError:
        sys.stderr.write('Error parsing review:\n\n%s\n' % repr(cell))

def partition(pred, iterable):
    """Use a predicate to partition entries into false entries and true entries"""
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    t1, t2 = itertools.tee(iterable)
    return itertools.ifilterfalse(pred, t1), filter(pred, t2)

def _preprocess_reviews(reviews, sheetname):
    pred = lambda (idx, cell): repr(cell).startswith('error:')
    good, bad = partition(pred, enumerate(reviews))

    for idx, review in bad:
        sys.stderr.write('Error on row %d in sheet "%s". Ignoring row.\n' % (idx+1, sheetname))

    return [review for idx, review in good]

def tokenize_many(xlsxpath, review_index=1):
    raws = []

    with xlrd.open_workbook(xlsxpath) as book:
        for sheet in book.sheets():
            sys.stderr.write('Parsing sheet %s\n' % sheet.name)
            # NOTE: to be removed when format is agreed upon.
            if sheet.name == u'all real ':
                reviews = sheet.col(3)
            else:
                reviews = sheet.col(review_index)

            reviews = _preprocess_reviews(reviews, sheet.name)
            raws.extend(loadcells(reviews))

    return '\n'.join(raws)

def tokenize(xlsxpath):
    return word_tokenize(tokenize_many(xlsxpath))

def remove_stopwords(tokens, stopwords):
    return [token for token in tokens if token not in stopwords]

def _build_stopword_list(stopword_list_path):
    with open(stopword_list_path) as f:
        return {x.strip().lower() for x in f}

def ubtgrams(tokens, word_categories=None):
    grams = defaultdict(itertools.count().next)
    freq = defaultdict(int)

    # get single tokens before ngramming
    if word_categories:
        tokens = [word_categories.get((token, ), token) for token in tokens]

    for n in [1, 2, 3]:
        for ngram in ngrams(tokens, n):
            if word_categories:
                ngram = word_categories.get(ngram, ngram)
            _ = grams[ngram]
            freq[ngram] += 1

    return dict(grams), dict(freq)

def skipgram_all(tokens, skipmax, word_categories=None):
    assert(skipmax >= 1)
    grams = defaultdict(itertools.count().next)

    # get single tokens before skipgramming
    if word_categories:
        tokens = [word_categories.get((token, ), token) for token in tokens]

    # find skipgrams, annotate with skip value
    sgrams = zip(skipgrams(tokens, 2, skipmax), itertools.cycle(range(0, skipmax + 1)))
    # ignore bigrams without a skip
    sgrams = [x for x in sgrams if x[1] != 0]

    # get counts, keeping track of skip value
    sgram_freq = Counter(sgrams)

    # get unigrams for outputting the master list
    for ngram in ngrams(tokens, 1):
        _ = grams[ngram]

    # return sgrams without skip value for easy iteration & printing
    # when outputting part 2
    return grams, {x[0] for x in sgrams}, sgram_freq

def _load_categorizer(category_tsv):
    word_categories = {}
    with open(category_tsv) as f:
        _ = f.readline()
        for line in f:
            tokens, category = line.lower().strip().split('\t')
            grams = tuple(tokens.split())
            word_categories[grams] = category

    return word_categories

def _save_part_one(grams, freq, outpath):
    with open(outpath, 'w') as out:
        out.write('label\twords\tcount\n')
        for gram, uid in grams.iteritems():
            out.write('%d\t%s\t%d\n' % (uid, ' '.join(gram), freq[gram]))

def _save_part_two(grams, sgrams, sgram_freq, skipmax,
                   freq_outpath):
    with open(freq_outpath, 'w') as out:
        fields = ['word 1', 'word 2']
        fields.extend(['gap%d_freq' % x for x in range(1, skipmax + 1)])
        out.write('%s\n' % '\t'.join(fields))

        for token1, token2 in sgrams:
            fields = [grams[(token1,)], grams[(token2,)]]
            for skip in range(1, skipmax + 1):
                fields.append(sgram_freq[((token1, token2), skip)])

            out.write('%s\n' % '\t'.join(map(str, fields)))

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] input.xlsx"
    parser = OptionParser(usage=usage)
    parser.add_option('-s', '--stopword-list', default='data/stopwords.txt',
                      help='Stopword list to use (one word per line; only lowercase)')
    parser.add_option('--category-word-list', default='data/category_words.tsv',
                      help='Category word list to use (TAB separated, 1 line header, wordTABcategory)')
    parser.add_option('-c', '--use-categories', default=False, action='store_true',
                      help='Use categories')
    parser.add_option('-m', '--skip-max', default=3, type='int',
                      help='Maximum skip to consider [default: %default]')

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 2

    xlsxdir = os.path.dirname(args[0])
    xlsxname = os.path.basename(args[0]).replace('.xlsx', '').replace('.XLSX', '')
    outdir = os.path.join(xlsxdir, xlsxname)

    try:
        os.mkdir(outdir)
    except OSError:
        sys.stderr.write('%s already exists! Files will be overwritten.\n' % outdir)

    # do stuff
    stopwords = _build_stopword_list(options.stopword_list)
    tokens = remove_stopwords(tokenize(args[0]), stopwords)

    if options.use_categories:
        sys.stderr.write('Using category file: %s...\n' %
                         options.category_word_list)
        word_categories = _load_categorizer(options.category_word_list)
    else:
        word_categories = None

    grams, freq = ubtgrams(tokens, word_categories)
    _save_part_one(grams, freq, os.path.join(outdir, 'master-wordlist.tsv'))
    
    _, sgrams, sgram_freq = skipgram_all(tokens, options.skip_max,
                                         word_categories)
    _save_part_two(grams, sgrams, sgram_freq, options.skip_max,
                   os.path.join(outdir, 'part2-freq.tsv'))

if __name__ == '__main__':
    sys.exit(main())
