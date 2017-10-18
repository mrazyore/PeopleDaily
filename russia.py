# encoding: utf-8

'''

@author: ZiqiLiu


@file: russia.py

@time: 2017/10/17 上午11:19

@desc:
'''

# combine russia and soviet
from glob import glob
import os

russia_scores = glob('./scores/俄罗斯/*.csv')
print(len(russia_scores))
count = 0
for fi in russia_scores:
    for i in range(1946, 1992):
        if str(i) in fi:
            count += 1


with open('./percents/俄罗斯percent.csv', 'r') as f:
    percent_russia = [line.strip() for line in f]

with open('./percents/苏联percent.csv', 'r') as f:
    percent_soviet = [line.strip() for line in f]

print(len(percent_russia))
print(len(percent_soviet))

combine_percent = percent_soviet[:46] + percent_russia[count:]
print(len(combine_percent))

with open('./percents/俄罗斯percent.csv', 'w') as f:
    for p in combine_percent:
        f.write(p + '\n')

for year in range(1946, 1992):
    os.system('mv ./scores/苏联/苏联_%d.csv ./scores/俄罗斯/俄罗斯_%d.csv' % (year, year))