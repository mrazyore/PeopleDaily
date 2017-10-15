# -*- coding: utf-8 -*-
import codecs

wordmap = {}


def mapPolarity(polarity):
    if polarity > 2:
        return 0
    if polarity == 2:
        return -1
    else:
        return polarity


with codecs.open('wordmap.txt', 'r', 'utf-8') as f:
    for line in f:
        columns = line.split('\t')
        wordmap[columns[0]] = mapPolarity(int(columns[6])) * int(columns[5])


def cal_score(wc):
    total = 0
    # print 'calculating score......'
    for key in wc:
        score = wordmap.get(key, 0)
        total += score * wc[key]
    # print total
    return total


def cal_score_test(wc):
    for key in wc:
        # if key in stop_word:
        #     return None
        score = wordmap.get(key, 0)
        if score<0:
            print(key,score,wc[key])

