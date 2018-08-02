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

def fixJpg(src, res):
  with open(src, 'rb') as source:
    rdr = csv.reader(source, delimiter=',')
    with open(res, 'wb') as result:
      wtr = csv.writer(result)
      for r in rdr:
        if r[11] == '.jpg':
          url = r[10]
          if url.startswith('https://stockx-360.imgix.net/'):
            trim1 = r"(.*?)"
            trim2 = r"https://stockx-360.imgix.net/(.*?)/"
            image_source = ''.join(url)
            image_filename = ''.join(re.findall(trim2,url)) + '.jpg'
            r[10] = image_source
            r[11] = image_filename
          wtr.writerow(r[0:12])

def faultyToNull(src1, src2, res):
  faulty = set()
  with open(src1, 'rb') as source1:
    rdr1 = csv.reader(source1, delimiter=',')
    for r1 in rdr1:
      faulty.add(r1[0])
      print 'added to set: ' + str(r1[0])
      print 'set length: ' , len(faulty)
  with open(src2, 'rb') as source2:
    rdr2 = csv.reader(source2, delimiter=',')
    with open(res, 'wb') as result:
      wtr = csv.writer(result)
      count = 0
      for r2 in rdr2:
        if str(r2[10]) in faulty:
          count = count + 1
          print 'found faulty: ', count, ' ', r2[10]
          r2[10] = 'null'
        wtr.writerow(r2)

def compareTotal(src1, src2, res):
  downloaded = set()
  with open(src1, 'rb') as source1:
    rdr1 = csv.reader(source1, delimiter=',')
    for r1 in rdr1:
      downloaded.add(str(r1[0]))
      print 'added to set: ' + str(r1[0])
      print 'set length: ' , len(downloaded)
  with open(src2, 'rb') as source2:
    rdr2 = csv.reader(source2, delimiter=',')
    with open(res, 'wb') as result:
      wtr = csv.writer(result)
      count = 0
      for r2 in rdr2:
        if str(r2[11]) in downloaded:
          count = count + 1
      print 'valid filenames : ', count
        # wtr.writerow(r2)

# fixJpg("../stockxData/result8.csv", "../stockxData/result9.csv")
# faultyToNull('../stockxData/faultyUrl.csv', '../stockxData/result8.csv', '../stockxData/result9.csv')
compareTotal('../stockxData/updatedNames.csv', '../stockxData/result9.csv', '../stockxData/result10.csv')

# with open('../stockxData/result9.csv', 'rb') as source1:
#   rdr1 = csv.reader(source1, delimiter=',')
#   with open('../stockxData/updatedNames.csv', 'rb') as source2:
#     rdr2 = csv.reader(source2, delimiter=',')
#     count1 = 0
#     count2 = 0
#     for r1 in rdr1:
#       # if 'null' == str(r1[10]):
#       count1 = count1 + 1
#     print count1 
#     for r2 in rdr2:
#       if r2[0] == '.jpg':
#         count2 = count2 - 1
#       count2 = count2 + 1
#     print count2


