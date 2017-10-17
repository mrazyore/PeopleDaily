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

for year in range(1946, 1992):
    os.system('mv ./scores/苏联/苏联_%d.csv ./scores/俄罗斯/俄罗斯_%d.csv' % (year, year))

with open('./percents/俄罗斯percent.csv', 'r') as f:
    percent_russia = [line for line in f]

with open('./percents/苏联percent.csv', 'r') as f:
    percent_soviet = [line for line in f]

print(len(percent_russia))
print(len(percent_soviet))
