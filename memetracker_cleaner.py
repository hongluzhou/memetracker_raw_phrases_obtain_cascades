#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 00:10:24 2019

@author: honglu
"""

import os
import gzip
import pickle
import pandas as pd
import datetime
from datetime import datetime as dt
import pdb
import numpy as np

"""
memetracker data cleaner

https://snap.stanford.edu/data/memetracker9.html
"""


def create_config():
    config = {
                'rawfiles': ['./raw/memetracker/quotes_2008-08.txt.gz',
                             './raw/memetracker/quotes_2008-09.txt.gz',
                             './raw/memetracker/quotes_2008-10.txt.gz',
                             './raw/memetracker/quotes_2008-11.txt.gz',
                             './raw/memetracker/quotes_2008-12.txt.gz',
                             './raw/memetracker/quotes_2009-01.txt.gz',
                             './raw/memetracker/quotes_2009-02.txt.gz',
                             './raw/memetracker/quotes_2009-03.txt.gz',
                             './raw/memetracker/quotes_2009-04.txt.gz'
                             ],
                'output_path': './data/memetracker_dataset/',

                'site_cutoff': 5000,
                'meme_cutoff': 10000
             }
    return config


config = create_config()
if not os.path.exists(config['output_path']):
    os.makedirs(config['output_path'])


def get_one_cascade_pandas(df, meme):
    df_meme = pd.DataFrame(df.get_group(meme))
    df_meme.sort_values(by=['time'], inplace=True, ascending=True)
    df_meme.drop_duplicates('site')
    return df_meme


if __name__ == '__main__':

    """
    Load raw dataset
    """
    print(".............. Load raw dataset")
    print(config['rawfiles'])

    print("starting reading raw dataset")
    lines = []
    count = 0
    for file in config['rawfiles']:
        with gzip.open(file, 'rt') as f:
            for line in f:
                lines.append(line)
        count += 1
        print(count, len(config['rawfiles']))

    with open(os.path.join(config['output_path'], "lines.pickle"), 'wb') as f:
        pickle.dump(lines, f)

    print(" ")

    """
    Get site frequency and choose cut off
    """
    print(".............. Get site frequency and choose cut off")
    site_frequency = dict()

    for line in lines:
        if line == '\n':
            continue
        [tag, content] = line.split('\n')[0].split('\t')
        if tag == 'P':
            site = content.split('http://')[1].split('/')[0]
            try:
                site_frequency[site] += 1
            except KeyError:
                site_frequency[site] = 1

    sort_site_frequency = sorted(list(site_frequency.values()), reverse=True)
    print('the number of sites:')
    print(len(site_frequency))
    print('top 10 sites frequency:')
    print(sort_site_frequency[:10])
    print('last 10 sites frequency:')
    print(sort_site_frequency[-10:])
    print('site frequency cut off:')
    print(config['site_cutoff'])
    print('site cutoff point frequency:')
    print(sort_site_frequency[config['site_cutoff']])

    allsites = set()
    for site in site_frequency:
        if site_frequency[site] >= sort_site_frequency[config['site_cutoff'] - 1]:
            allsites.add(site)
            if len(allsites) >= config['site_cutoff']:
                break
    print("allsites len:")
    print(len(allsites))

    print(" ")

    """
    Get memes frequency and choose cut off
    """
    print(".............. Get memes frequency and choose cut off")
    Q_oc = dict()
    for line in lines:
        if line == '\n':
            continue
        [tag, content] = line.split('\n')[0].split('\t')
        if tag == 'Q':
            try:
                Q_oc[content] += 1
            except KeyError:
                Q_oc[content] = 1

    sort_q_oc = sorted(list(Q_oc.values()), reverse=True)
    print('the number of memes:')
    print(len(Q_oc))
    print('top 10 memes frequency:')
    print(sort_q_oc[:10])
    print('last 10 memes frequency:')
    print(sort_q_oc[-10:])
    print('meme frequency cut off:')
    print(config['meme_cutoff'])
    print('meme cutoff point frequency:')
    print(sort_q_oc[config['meme_cutoff']])

    allmeme = set()
    for meme in Q_oc:
        if Q_oc[meme] >= sort_q_oc[config['meme_cutoff'] - 1]:
            allmeme.add(meme)
            if len(allmeme) >= config['meme_cutoff']:
                break
    print("allmeme len:")
    print(len(allmeme))

    print(" ")

    """
    Get the first index of each post/article whose site satifies the site cut off requirement
    """
    print(".............. Get the first index of each post/article whose site satifies the site cut off requirement")
    blogs_start_line_idx = []
    for i in range(len(lines)):
        line = lines[i]
        if line == '\n':
            continue
        else:
            [tag, content] = line.split('\n')[0].split('\t')
            if tag == 'P':
                site = content.split('http://')[1].split('/')[0]
                if site in allsites:
                    blogs_start_line_idx.append(i)
    print("blogs_start_line_idx len:")
    print(len(blogs_start_line_idx))

    print(" ")

    """
    Create cascades pandas dataframe and save
    """
    print(".............. Create cascades pandas dataframe and save")
    meme_cascades = dict()
    meme_cascades['meme'] = []
    meme_cascades['time'] = []
    meme_cascades['site'] = []
    allsite_new = set()
    allmeme_new = set()

    for i in range(len(blogs_start_line_idx)):
        idx = blogs_start_line_idx[i]
        try:
            next_idx = blogs_start_line_idx[i + 1]
        except IndexError:
            next_idx = len(lines)
        blogmemes = []
        # print(idx, next_idx)
        # print(lines[idx])
        # print(lines[next_idx])

        for blogidx in range(idx, next_idx - 1):
            line = lines[blogidx]
            if line == '\n':
                break
            [tag, content] = line.split('\n')[0].split('\t')
            # print(line)
            if tag == 'P':
                site = content.split('http://')[1].split('/')[0]
            if tag == 'Q':
                blogmemes.append(content)
            if tag == 'T':
                blogtime = content
        # print(len(blogmemes))
        for meme in blogmemes:
            if meme in allmeme:
                meme_cascades['meme'].append(meme)
                meme_cascades['time'].append(blogtime)
                meme_cascades['site'].append(site)

                allsite_new.add(site)
                allmeme_new.add(meme)
        # print(meme_cascades['meme'])
        # print(meme_cascades['time'])
        # print(meme_cascades['site'])
    allsite = allsite_new
    allmeme = allmeme_new
    print("allsite len:")
    print(len(allsite))
    print("allmeme len:")
    print(len(allmeme))

    del lines

    df = pd.DataFrame(meme_cascades)
    df.to_csv(os.path.join(config['output_path'], "cascades_meme_origial_timeformat_df.csv"), index=False)
    print("df len:")
    print(len(df))
    df['time'] = pd.to_datetime(df['time'], format="%Y-%m-%d %H:%M:%S")
    df.sort_values(by=['time'], inplace=True, ascending=True)
    df.to_csv(os.path.join(config['output_path'], "cascades_meme_datetime_timeformat_df.csv"), index=False)

    print(" ")

    """
    Create and save uid_uname_D0.pickle & uid_uname_reverse_D0.pickle
    """
    print(".............. Create and save uid_uname_D0.pickle & uid_uname_reverse_D0.pickle")
    site2id = dict()
    id2site = dict()

    for site in allsite:
        id2site[len(site2id)] = site
        site2id[site] = len(site2id)
    print("site2id len:")
    print(len(site2id))
    print("id2site len:")
    print(len(id2site))

    with open(os.path.join(config['output_path'], "uid_uname_D0.pickle"), 'wb') as f:
        pickle.dump(id2site, f)
    with open(os.path.join(config['output_path'], "uid_uname_reverse_D0.pickle"), 'wb') as f:
        pickle.dump(site2id, f)

    print(" ")

    """
    Create and save infoid_infoname_D0.pickle & infoid_infoname_reverse_D0.pickle
    """
    print(".............. Create and save infoid_infoname_D0.pickle & infoid_infoname_reverse_D0.pickle")
    info2id = dict()
    id2info = dict()

    for meme in allmeme:
        id2info[len(info2id)] = meme
        info2id[meme] = len(info2id)
    print("info2id len:")
    print(len(info2id))
    print("id2info len:")
    print(len(id2info))

    with open(os.path.join(config['output_path'], "infoid_infoname_D0.pickle"), 'wb') as f:
        pickle.dump(id2info, f)
    with open(os.path.join(config['output_path'], "infoid_infoname_reverse_D0.pickle"), 'wb') as f:
        pickle.dump(info2id, f)

    print(" ")

    """
    Create and save diffpath_user_D0.pickle, diffpath_time_D0.pickle, diffpath_info_D0.pickle, diffpath_info_reverse_D0.pickle
    """
    print(".............. Create and save diffpath_user_D0.pickle, diffpath_time_D0.pickle, diffpath_info_D0.pickle, diffpath_info_reverse_D0.pickle")
    diffpath_user_D0 = []
    diffpath_time_D0 = []
    diffpath_info_D0 = dict()
    diffpath_info_reverse_D0 = dict()
    # diffpath_content_D0 = dict()
    # diffpath_content_reverse_D0 = dict()
    df = df.groupby('meme')
    for meme in allmeme:
        df_meme = get_one_cascade_pandas(df, meme)
        diffpath_user_this = list(df_meme['site'])
        diffpath_time_this = list(df_meme['time'])
        diffpath_info_D0[len(diffpath_user_D0)] = meme
        diffpath_info_reverse_D0[meme] = [len(diffpath_user_D0)]
        # pdb.set_trace()

        diffpath_user_D0.append(diffpath_user_this)
        diffpath_time_D0.append(diffpath_user_this)

    print("diffpath_user_D0 len:")
    print(len(diffpath_user_D0))
    print("diffpath_time_D0 len:")
    print(len(diffpath_time_D0))
    print("diffpath_info_D0 len:")
    print(len(diffpath_info_D0))
    print("diffpath_info_reverse_D0 len:")
    print(len(diffpath_info_reverse_D0))

    with open(os.path.join(config['output_path'], "diffpath_user_D0.pickle"), 'wb') as f:
        pickle.dump(diffpath_user_D0, f)
    with open(os.path.join(config['output_path'], "diffpath_time_D0.pickle"), 'wb') as f:
        pickle.dump(diffpath_time_D0, f)
    with open(os.path.join(config['output_path'], "diffpath_info_D0.pickle"), 'wb') as f:
        pickle.dump(diffpath_info_D0, f)
    with open(os.path.join(config['output_path'], "diffpath_info_reverse_D0.pickle"), 'wb') as f:
        pickle.dump(diffpath_info_reverse_D0, f)
