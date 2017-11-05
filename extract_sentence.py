# -*- coding: utf-8 -*-

# extract all articles for specific country

from glob2 import glob
import json
import codecs


try:
    from tqdm import tqdm  # long waits are not fun XD
except:
    print('TQDM does make much nicer wait bars...')
    tqdm = lambda x: x

json_path = './json/**/'

file_list = glob(json_path + "*.json")
print(str(len(file_list)) + ' json file loaded.')

target_country = ['美国', '美帝']

country = set(target_country)


def processing(f_list):
    articles = []
    for file in tqdm(f_list):

        print('processing ' + file + '...')
        with codecs.open(file, 'r', "utf-8") as json_file:
            data = json.load(json_file)

            for article in data:  # 30天
                contents = article['contents']
                whole = '。'.join(contents)
                for c in country:
                    if c in whole:
                        articles.append(whole)
    return articles


if __name__ == '__main__':
    articles = processing(file_list)
    with open('extract.txt', 'w') as f:
        for a in articles:
            f.write(a + '\n')
