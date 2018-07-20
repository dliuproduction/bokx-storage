import csv
import json
import glob
import os
import shutil
import sys
import re
import logging
import urllib2
from more_itertools import unique_everseen

# http client configuration
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/63.0.3239.84 Chrome/63.0.3239.84 Safari/537.36'

# logging configuration
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

python_version = sys.version_info.major
logging.info("executed by python %d" % python_version)

faultyUrl = []

# compatability with python 2
if python_version == 3:
    import urllib.parse
    import urllib.request
    urljoin = urllib.parse.urljoin
    urlretrieve = urllib.request.urlretrieve
    quote = urllib.parse.quote

    # configure headers
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', user_agent)]
    urllib.request.install_opener(opener)
else:
    import urlparse
    import urllib
    urljoin = urlparse.urljoin
    urlretrieve = urllib.urlretrieve
    quote = urllib.quote

    # configure headers
    class AppURLopener(urllib.FancyURLopener):
        version = user_agent
    urllib._urlopener = AppURLopener()

def merge(headerFile, outFile):
  fout = open("out.txt","a")
  # first file:
  first = open(headerFile)
  fout.write(first.readline())

  # now the rest:    
  for filename in glob.glob('*.csv'):
    f = open(filename)
    print ('merging ' + filename)
    f.next() # skip the header
    for line in f:
      fout.write(line)
    f.close() # not really needed
  fout.close()
  os.rename('out.txt', outFile)

def trim(src, res):
  with open(src, 'rb') as source:
    rdr = csv.reader(source, delimiter=',')
    with open(res, 'wb') as result:
      wtr = csv.writer(result)
      for r in rdr:
        wtr.writerow( (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]))

def correct(src, res):
  with open(src, 'rb') as source:
    rdr = csv.reader(source, delimiter=',')
    with open(res, 'wb') as result:
      wtr = csv.writer(result)
      for r in rdr:
        newRow = [r[0], '', '', '', '', r[5], r[6], r[7], r[8], r[9], r[10]]
        for i in range(1, 5):
          if r[i] == r[5] or r[i] == 'null' or r[i] == '' or r[i] == None:
            newRow[i] = 'null'
          else:
            newRow[i] = r[i]
        wtr.writerow(newRow)

def getImages(src, res):
  with open(src, 'rb') as source:
    rdr = csv.reader(source, delimiter=',')
    with open(res, 'wb') as result:
      wtr = csv.writer(result)
      for r in rdr:
        row = [r[10]]
        wtr.writerow(row)
        print r[10]

def labelImages(src, res):
  with open(src, 'rb') as source:
    rdr = csv.reader(source, delimiter=',')
    with open(res, 'wb') as result:
      wtr = csv.writer(result)
      for r in rdr:
        if not ('jpg' in r[10] or 'jpeg' in r[10] or 'png' in r[10] or r[10] == 'null'):
          r[10] = r[10] + '.png'
          print ('added suffix to ' + r[10])
        url = r[10]
    
        if url.startswith('https://stockx.imgix.net/'):
          trim1 = r"(.*?)"
          trim2 = r"https://stockx.imgix.net/(.*)"
          image_source = ''.join(url)
          image_filename = ''.join(re.findall(trim2,url))
          r[10] = image_source
          r[11] = image_filename
        elif url.startswith('https://stockx-360.imgix.net/'):
          suffix = ''
          if '.jpg' in url:
            suffix = '.jpg'
          else:
            suffix = '.png'
          trim1 = r"(.*?)"
          trim2 = r"https://stockx-360.imgix.net/(.*?)_TruView"
          image_source = ''.join(url)
          image_filename = ''.join(re.findall(trim2,url)) + suffix
          r[10] = image_source
          r[11] = image_filename
        else:
          r[10] = 'null'
          r[11] = 'null'
        wtr.writerow(r[0:12])

# labelImages()

with open('stockxData/result7.csv', 'rb') as source, open('result8.csv','w') as result:
    result.writelines(unique_everseen(source))
    
with open('stockxData/result8.csv', 'rb') as source:
  rdr = csv.reader(source, delimiter=',')
  count = 0
  for r in rdr:
    # if not ('jpg' in r[10] or 'jpeg' in r[10] or 'png' in r[10] ):
    # if r[10] == 'https://stockx.imgix.net/Reebok-Answer-IV-Kobe-Bryant-PE.png':
    # if not os.path.isfile('result7/' + r[11]) and r[11] != 'null':
    count += 1
    print count
    print r[11]
# trim2 = r"https://stockx.imgix.net/(.)"
# url = 'https://stockx.imgix.net/Under-Armour-Curry-5-White.png'
# print ''.join(re.findall(trim2,url))
# print url
# listUrl = list(url)
# listUrl[25] = url[25].swapcase()
# print ''.join(listUrl)
# new_url = url.replace('.png', '.jpg')
# print url
# print new_url
# response = urllib2.urlopen("https://stockx.imgix.net/Adidas-Superstar-Captain-Tsubasa.png")
# info = response.info()
# for header in info.headers:
#     print header
