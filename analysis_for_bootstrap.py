# -*- coding: utf-8 -*-
from __future__ import division
from glob2 import glob
import json
import os
import codecs
import thulac
from multiprocessing import Pool
import multiprocessing
from functools import reduce

try:
    from tqdm import tqdm  # long waits are not fun XD
except:
    print('TQDM does make much nicer wait bars...')
    tqdm = lambda x: x
from WordsMap import *

lac = thulac.thulac(seg_only=True)

json_path = './json/**/'

file_list = glob(json_path + "*.json")
print(str(len(file_list)) + ' json file loaded.')

with codecs.open('country.txt', 'r', 'utf-8') as f:
    countries = [line.strip() for line in f]

# alias mode ----------------------------------------------
countries_set = set(countries)
# must ensure that alias name in alias.txt are aligned with the country.txt
with codecs.open('country_alias.txt', 'r', 'utf-8') as f:
    alias = [line.strip().split(',') for line in f]
alias.extend([[]] * (len(countries) - len(alias)))

alias_map = {}
for i, l in enumerate(alias):
    for alia in l:
        alias_map[alia] = countries[i]
# alias mode ----------------------------------------------
years = range(1946, 2016)


def count(text):
    word_count = {}

    words = lac.cut(text)
    for word in words:
        if word[0] in word_count:
            word_count[word[0]] += 1
        else:
            word_count[word[0]] = 1
    return word_count


def processing(i, multi_score, multi_country_count, multi_total_count, f_list):
    # ---------------------------------------
    # score_map[country][year] = [a list of score]
    score_map = {}
    for c in countries_set:
        score_map[c] = {}
    # ---------------------------------------
    country_count = {}
    for c in countries_set:
        country_count[c] = {}
    # ---------------------------------------
    total_count = {}
    for y in years:
        total_count[y] = 0
    # ---------------------------------------

    for file in tqdm(f_list):
        print('processing ' + file + '...')
        with codecs.open(file, 'r', "utf-8") as json_file:
            data = json.load(json_file)
            year = int(data[0]['metadata']['date']['year'])

            for article in data:  # 30天
                contents = article['contents']
                countryList = {}
                whole = '。'.join(contents)
                if '我国' in whole or '中国' in whole or '中方' in whole:
                    for sentence in contents:
                        appear = set()
                        for c in countries_set:
                            if c in sentence:
                                appear.add(c)
                        for c in alias_map:
                            if c in sentence:
                                appear.add(alias_map[c])
                        appear_list = set(appear)

                        if len(appear_list) == 1 or (
                                '印尼' in appear_list and len(appear_list) == 2):
                            # we only calculate those sentence
                            # with exactly one country
                            cc = appear_list.pop()
                            if cc in countryList:
                                countryList[cc] += '。' + sentence
                            else:
                                countryList[cc] = sentence

                    # a map contains corresponding sentence with countries
                    if len(countryList) > 0:
                        total_count[year] += 1
                        for c in countryList:
                            wc = count(countryList[c])
                            score = cal_score(wc)
                            if score:
                                if year in score_map[c]:
                                    score_map[c][year].append(score)
                                else:
                                    score_map[c][year] = [score]
                                if year in country_count[c]:
                                    country_count[c][year] += 1
                                else:
                                    country_count[c][year] = 1

    # return score_map
    multi_score[i] = score_map
    multi_country_count[i] = country_count
    multi_total_count[i] = total_count


def merge_score(map1, map2):
    for c in map1:
        for year in map1[c]:
            if year in map2[c]:
                map2[c][year].extend(map1[c][year])
            else:
                map2[c][year] = map1[c][year]
    return map2


def merge_count(map1, map2):
    for c in map1:
        for year in map1[c]:
            if year in map2[c]:
                map2[c][year] += map1[c][year]
            else:
                map2[c][year] = map1[c][year]
    return map2


def merge_total_count(map1, map2):
    for y in map1:
        map2[y] += map1[y]

    return map2


def cal_percentage(country_count, total_count):
    '''
    
    :param country_count: map[c][y]
    :param total_count: map[y]
    :return: map[c][y]
    '''
    result = {}
    for c in country_count:
        result[c] = {}
        for y in country_count[c]:
            result[c][y] = country_count[c][y] / total_count[y]
    return result


def div_list(l, n):
    length = len(l)
    t = length // n
    quaters = [t * i for i in range(0, n)]
    ran = range(0, n - 1)
    result = [l[quaters[i]:quaters[i + 1]] for i in ran]
    result.append(l[quaters[n - 1]:len(l)])
    return result


def multi():
    process_num = 4

    div_files = div_list(file_list, process_num)
    print(div_files)
    print('started')

    # scores=processing(0, [1], file_list)


    mgr = multiprocessing.Manager()
    multi_score = mgr.list(range(process_num))
    multi_article_count = mgr.list(range(process_num))
    multi_total_count = mgr.list(range(process_num))

    p = Pool()

    for i in range(process_num):
        p.apply_async(processing, args=(
            i, multi_score, multi_article_count, multi_total_count,
            div_files[i]))
    p.close()
    p.join()

    # scores[c][y] = [list of scores]
    scores = reduce(merge_score, multi_score)
    country_counts = reduce(merge_count, multi_article_count)
    total_counts = reduce(merge_total_count, multi_total_count)

    percentage = cal_percentage(country_counts, total_counts)
    if os.path.exists('./scores'):
        os.system('rm -r ./scores')
    os.mkdir('./scores')
    for c in scores:
        os.mkdir('./scores/' + c)
        for y in scores[c]:
            with open('./scores/%s/%s_%d.csv' % (c, c, y), 'w') as f:
                for s in scores[c][y]:
                    f.write(str(s) + '\n')
    if os.path.exists('./percents'):
        os.system('rm -r ./percents')
    os.mkdir('./percents')
    for c in percentage:
        c_percents = [p[1] for p in
                      sorted(list(percentage[c].items()), key=lambda d: d[0])]
        with open('./percents/%spercent.csv' % c, 'w') as f:
            for p in c_percents:
                f.write(str(p) + '\n')

    country_article_count = {}
    for c in country_counts:
        if len(country_counts[c]) == 0:
            country_article_count[c] = 0
        else:
            country_article_count[c] = sum(
                list(country_counts[c].values())) / len(country_counts[c])
    country_article_count = sorted(list(country_article_count.items()),
                                   key=lambda a: a[1], reverse=True)
    with open('article_count.txt', 'w') as f:
        for pair in country_article_count:
            f.write('%s %d\n' % (pair[0], pair[1]))


if __name__ == '__main__':
    multi()
