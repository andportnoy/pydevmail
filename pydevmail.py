#!/usr/local/bin/python3

import requests_html
import urllib
from multiprocessing import Pool
import os
import shutil
import gzip
import argparse

# the first and only argument is the link to the mailman archives page
parser = argparse.ArgumentParser()
parser.add_argument('base_link', help='mailing list archive link', type=str)
args = parser.parse_args()
base_link = args.base_link

tokens = base_link.split('/')
name = tokens[-1] if tokens[-1] else tokens[-2]

print('Creating tmp directory...')
os.mkdir(name + '-tmp')
print('Entering tmp directory...')
os.chdir(name + '-tmp')
print('Obtaining download links...')
links = requests_html.HTMLSession().get(base_link).html.absolute_links

gz_links = [link for link in links if '.txt.gz' in link]
if not gz_links:
    raise ValueError('No gzipped text file links found on page.')

gz_files = [gz_link.split('/')[-1] for gz_link in gz_links]
args = zip(gz_links, gz_files)

print('Downloading', name, 'archives...')
pool = Pool(16)
pool.starmap(urllib.request.urlretrieve, args)
pool.close()
pool.join()

print('Creating archive...')
with open('../' + name + '.txt', 'wb') as out:
    for file in gz_files:
        with gzip.open(file, 'rb') as f:
            shutil.copyfileobj(f, out)

print('Cleaning up...')
for file in gz_files:
    os.remove(file)

os.chdir('..')
os.rmdir(name + '-tmp')
print('Done. Check file', name + '.txt.')
