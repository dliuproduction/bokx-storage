#! /usr/bin/env python3

import re
import csv
import json
import glob
import os
import shutil
import sys
import re
import logging
import urllib2
import time
import datetime
import base64
import hashlib
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from sets import Set
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

def uploadDatabase(row):

        # Use the application default credentials
    if (not len(firebase_admin._apps)):
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': 'bokx-fa37d',
        })

    db = firestore.client()

    shoeid = str(row[0])
    brand = str(row[1])
    series = str(row[2])
    model = str(row[3])
    version = str(row[4])
    name = str(row[5])
    style = str(row[6])
    colorway = str(row[7])
    retail_price = str(row[8])
    release_date = str(row[9])
    image_name = str(row[11])

    data = {
    u'shoeid': unicode(shoeid),
    u'brand': unicode(brand),
    u'series': unicode(series),
    u'model': unicode(model),
    u'version': unicode(version),
    u'name': unicode(name),
    u'style': unicode(style),
    u'colorway': unicode(colorway),
    u'retail_price': unicode(retail_price),
    u'release_date': unicode(release_date),
    u'image_name': unicode(image_name)
    }

    map_ref = db.collection(u'shoeMap').document(shoeid)
    map_ref.set(data)

    print 'uploaded shoe data: ', name

def uploadFiles(dest_dir, row):

    image_filename = row[11]
    image_path = os.path.join(dest_dir, image_filename)
    url = 'https://firebasestorage.googleapis.com/v0/b/bokx-fa37d.appspot.com/o/shoes%2F+' + image_filename
    if 'jpg' in image_filename or 'jpeg' in image_filename:
        headers = {'Content-Type': 'image/jpg'}
    elif 'png' in image_filename:
        headers = {'Content-Type': 'image/png'}
    else:
        return
    payload = open(image_path, 'rb')
    r = requests.post(url, headers=headers, data=payload)
    if r.status_code == 200:
        print 'uploaded file: ', image_filename
    else: 
        print 'error uploading: ', image_filename, '\n status code: ', str(r.status_code)
        return

def download_image(dest_dir, row):

    image_url = row[10]
    image_url = fix_url(image_url)
    image_filename = row[11]
    row[11] = 'null'
    try:

        fout = open("faultyUrl.csv","a")
        logging.info("downloading image %s" % image_url)
        tmp_file_name, headers = urlretrieve(image_url)
        content_type = headers.get("Content-Type")
        image_path = os.path.join(dest_dir, image_filename)
        oldSuffix = ''
        newSuffix = ''

        if content_type == 'image/jpeg' or content_type == 'image/jpg' or content_type == 'image/png' or content_type == 'image/gif':
          image_path = os.path.join(dest_dir, image_filename)
        elif content_type == 'text/plain':
            while content_type == 'text/plain':
                if 'https://stockx.imgix.net/' in image_url:
                    listUrl = list(image_url)
                    listUrl[25] = image_url[25].swapcase()
                    test_url = ''.join(listUrl)
                    logging.info("Faulty URL, trying download from %s" % test_url)
                    tmp_file_name, headers = urlretrieve(test_url)
                    content_type = headers.get("Content-Type")
                    if content_type == 'image/jpeg' or content_type == 'image/jpg' or content_type == 'image/png' or content_type == 'image/gif':
                        break
                    if '.jpeg' in image_url:
                        oldSuffix = '.jpeg'
                        test_url = image_url.replace('.jpeg', '.jpg')
                        logging.info("Faulty URL, trying download from %s" % test_url)
                        tmp_file_name, headers = urlretrieve(test_url)
                        content_type = headers.get("Content-Type")
                        if content_type == 'image/jpg':
                            newSuffix = '.jpg'
                            break
                        test_url = image_url.replace('.jpeg', '.png')
                        logging.info("Faulty URL, trying download from %s" % test_url)
                        tmp_file_name, headers = urlretrieve(test_url)
                        content_type = headers.get("Content-Type")
                        if content_type == 'image/png':
                            newSuffix = '.png'
                            break
                        logging.warning("unknown image content type: %s \n url: %s" % (content_type, image_url))
                        fout.write(image_url + '\n')
                        return row
                    elif '.jpg' in image_url:
                        oldSuffix = '.jpg'
                        test_url = image_url.replace('.jpg', '.jpeg')
                        logging.info("Faulty URL, trying download from %s" % test_url)
                        tmp_file_name, headers = urlretrieve(test_url)
                        content_type = headers.get("Content-Type")
                        if content_type == 'image/jpeg':
                            newSuffix = '.jpeg'
                            break
                        test_url = image_url.replace('.jpg', '.png')
                        logging.info("Faulty URL, trying download from %s" % test_url)
                        tmp_file_name, headers = urlretrieve(test_url)
                        content_type = headers.get("Content-Type")
                        if content_type == 'image/png':
                            newSuffix = '.png'
                            break
                        logging.warning("unknown image content type: %s \n url: %s" % (content_type, image_url))
                        fout.write(image_url + '\n')
                        return row
                    elif '.png' in image_url:
                        oldSuffix = '.png'
                        test_url = image_url.replace('.png', '.jpg')
                        logging.info("Faulty URL, trying download from %s" % test_url)
                        tmp_file_name, headers = urlretrieve(test_url)
                        content_type = headers.get("Content-Type")
                        if content_type == 'image/jpg':
                            newSuffix = '.jpg'
                            break
                        test_url = image_url.replace('.png', '.jpeg')
                        logging.info("Faulty URL, trying download from %s" % test_url)
                        tmp_file_name, headers = urlretrieve(test_url)
                        content_type = headers.get("Content-Type")
                        if content_type == 'image/jpeg':
                            newSuffix = '.jpeg'
                            break
                        logging.warning("unknown image content type: %s \n url: %s" % (content_type, image_url))
                        fout.write(image_url + '\n')
                        return row
                elif 'https://stockx-360.imgix.net/' in image_url:
                    listUrl = list(image_url)
                    listUrl[31] = image_url[31].swapcase()
                    test_url = ''.join(listUrl)
                    logging.info("Faulty URL, trying download from %s" % test_url)
                    tmp_file_name, headers = urlretrieve(test_url)
                    content_type = headers.get("Content-Type")

                    if content_type == 'image/jpeg' or content_type == 'image/jpg' or content_type == 'image/png' or content_type == 'image/gif':
                        break
                    if '.jpeg' in image_url:
                        oldSuffix = '.jpeg'
                        test_url = image_url.replace('.jpeg', '.jpg')
                        logging.info("Faulty URL, trying download from %s" % test_url)
                        tmp_file_name, headers = urlretrieve(test_url)
                        content_type = headers.get("Content-Type")
                        if content_type == 'image/jpg':
                            newSuffix = '.jpg'
                            break
                        test_url = image_url.replace('.jpeg', '.png')
                        logging.info("Faulty URL, trying download from %s" % test_url)
                        tmp_file_name, headers = urlretrieve(test_url)
                        content_type = headers.get("Content-Type")
                        if content_type == 'image/png':
                            newSuffix = '.png'
                            break
                        logging.warning("unknown image content type: %s \n url: %s" % (content_type, image_url))
                        fout.write(image_url + '\n')
                        return row
                    elif '.jpg' in image_url:
                        oldSuffix = '.jpg'
                        test_url = image_url.replace('.jpg', '.jpeg')
                        logging.info("Faulty URL, trying download from %s" % test_url)
                        tmp_file_name, headers = urlretrieve(test_url)
                        content_type = headers.get("Content-Type")
                        if content_type == 'image/jpeg':
                            newSuffix = '.jpeg'
                            break
                        test_url = image_url.replace('.jpg', '.png')
                        logging.info("Faulty URL, trying download from %s" % test_url)
                        tmp_file_name, headers = urlretrieve(test_url)
                        content_type = headers.get("Content-Type")
                        if content_type == 'image/png':
                            newSuffix = '.png'
                            break
                        logging.warning("unknown image content type: %s \n url: %s" % (content_type, image_url))
                        fout.write(image_url + '\n')
                        return row
                    elif '.png' in image_url:
                        oldSuffix = '.png'
                        test_url = image_url.replace('.png', '.jpg')
                        logging.info("Faulty URL, trying download from %s" % test_url)
                        tmp_file_name, headers = urlretrieve(test_url)
                        content_type = headers.get("Content-Type")
                        if content_type == 'image/jpg':
                            newSuffix = '.jpg'
                            break
                        test_url = image_url.replace('.png', '.jpeg')
                        logging.info("Faulty URL, trying download from %s" % test_url)
                        tmp_file_name, headers = urlretrieve(test_url)
                        content_type = headers.get("Content-Type")
                        if content_type == 'image/jpeg':
                            newSuffix = '.jpeg'
                            break
                        logging.warning("unknown image content type: %s \n url: %s" % (content_type, image_url))
                        fout.write(image_url + '\n')
                        return row
                else:
                    logging.warning("unknown image content type: %s \n url: %s" % (content_type, image_url))
                    fout.write(image_url + '\n')
                    return row
        else:
            logging.warning("unknown image content type: %s \n url: %s" % (content_type, image_url))
            fout.write(image_url + '\n')
            return row

        image_path.replace(oldSuffix, newSuffix)
        image_filename.replace(oldSuffix, newSuffix)
        shutil.move(tmp_file_name, image_path)
        row[11] = image_filename
        return row
        
    except Exception as e:
      logging.warning("Image download error. %s" % e)
      return row

def fix_url(url):
    url = quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    return url

def get_csv_image_dir(csv_filename):

    base = os.path.basename(csv_filename)
    dir = os.path.splitext(base)[0]

    if not os.path.exists(dir):
        os.makedirs(dir)

    return dir

def labelImages(row):
  url = row[10]
  trim1 = r"(.*?)\?" 
  suffix = ''
  if '.jpg' in url:
    suffix = '.jpg'
  elif '.jpeg' in url:
    suffix = '.jpeg'
  elif '.png' in url:
    suffix = '.png'
  else: 
    row[10] = 'null'
    row[11] = 'null'
    return row
  if url.startswith('https://stockx.imgix.net/'):
    if '?' in url:
      image_source = ''.join(re.findall(trim1,url))
    else:
      image_source = ''.join(url)
    trim2 = r"https://stockx.imgix.net/(.*)"
    image_filename = ''.join(re.findall(trim2,image_source))
    row[10] = image_source
    row[11] = image_filename
  elif url.startswith('https://stockx-360.imgix.net/'):
    if '_TruView' in url:
      if '?' in url:
        image_source = ''.join(re.findall(trim1,url))
      else:
        image_source = ''.join(url)
      trim2 = r"https://stockx-360.imgix.net/(.*?)_TruView"
      image_filename = ''.join(re.findall(trim2,image_source)) + suffix
      row[10] = image_source
      row[11] = image_filename
    else:
      if '?' in url:
        image_source = ''.join(re.findall(trim1,url))
      else:
        image_source = ''.join(url)
      trim2 = r"https://stockx-360.imgix.net/(.*?)/"
      image_filename = ''.join(re.findall(trim2,image_source)) + suffix
      row[10] = image_source
      row[11] = image_filename
  else:
    row[10] = 'null'
    row[11] = 'null'
  print 'labeling image: ', row[11]
  return row

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

def hashShoe(row):
  shoeData = ''.join(row[1:10])
  shoeData = ''.join(shoeData.split())
  shoeId = base64.urlsafe_b64encode(hashlib.md5(shoeData).digest())
  print 'hashing with MD5 function: \n', shoeData, '\ngot shoeID: \n', shoeId
  row[0] = shoeId
  return row

def labelDate(row):
  now = datetime.datetime.now()
  date = now.strftime("%Y-%m-%d")
  print "labeling date_added, current date: ", date
  row.extend(['', ''])
  row[12] = date
  return row

def removeNull(row):
  newRow = [row[0], '', '', '', '', row[5], row[6], row[7], row[8], row[9], row[10]]
  for i in range(1, 5):
    if row[i] == row[5] or row[i] == 'null' or row[i] == '' or row[i] == None:
      newRow[i] = 'null'
    else:
      newRow[i] = row[i]
  print 'removing null'
  return newRow

def removeUnused(row):
    print 'removing unused columns'
    newRow = [row[0], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]]
    return newRow

def process(catalogSrc, entrySrc):

    catalogSet = set()
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    resultSrc = '../stockxData/' + date + '.csv'
    count = 0
    with open(catalogSrc, 'rb') as catalog:
        catalog_reader = csv.reader(catalog, delimiter=',')
        with open(entrySrc, 'rb') as entries:
            entries_reader = csv.reader(entries, delimiter=',')
            with open(resultSrc, 'wb') as result:
                writer = csv.writer(result)
                hout = ['shoe_id', 'brand', 'series', 'model', 'version', 'name', 'style', 'colorway', 'retail_price', 'release_date', 'image_src', 'image_name', 'date_added']
                writer.writerow(hout)

                catalog_reader.next()
                entries_reader.next()
                for row in catalog_reader:
                    catalogSet.add(row[0])
                    writer.writerow(row)

                dest_dir = get_csv_image_dir(entrySrc)

                for row in entries_reader:
                    
                    row = removeUnused(row)
                    row = removeNull(row)
                    row = labelDate(row)
                    row = hashShoe(row)
                    if row[0] in catalogSet:
                        continue
                    else:
                        count = count + 1
                        print 'Found new entry: ', count
                        row = labelImages(row)
                        row = download_image(dest_dir, row)
                        uploadFiles(dest_dir, row)
                        uploadDatabase(row)
                        catalogSet.add(row[0])
                        writer.writerow(row)

    shutil.copy(resultSrc, catalogSrc)

def customProcess(catalogSrc):

    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    resultSrc = '../stockxData/' + date + '.csv'
    count = 0
    with open(catalogSrc, 'rb') as catalog:
        catalog_reader = csv.reader(catalog, delimiter=',')
        with open(resultSrc, 'wb') as result:
            writer = csv.writer(result)
            hout = ['shoe_id', 'brand', 'series', 'model', 'version', 'name', 'style', 'colorway', 'retail_price', 'release_date', 'image_src', 'image_name', 'date_added']
            writer.writerow(hout)

            catalog_reader.next()
            for row in catalog_reader:
                row = labelDate(row)
                row = hashShoe(row)
                writer.writerow(row)
                uploadDatabase(row)
                count = count + 1
                print 'processed row: ', count
    shutil.copy(resultSrc, catalogSrc)

def main(args):

  # filename passde through args
    if len(args) >=3:
        catalog = args[1]
        entries = args[2]
        process(catalog, entries)
    elif len(args) >=2:
        catalog = args[1]
        customProcess(catalog)
    else:
        logging.warning("no input file found")

    time.sleep(20)

if __name__ == '__main__':
  main(sys.argv)