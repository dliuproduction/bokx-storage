#! /usr/bin/env python3

import csv
import shutil
import sys
import time
import os
import logging
import re

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

def fix_url(url):
    url = quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    return url


def download_csv_row_images(filename, dest_dir):

    #check whether csv file has utf-8 bom char at the beginning
    skip_utf8_seek = 0
    with open(filename, "rb") as csvfile:
        csv_start = csvfile.read(3)
        if csv_start == b'\xef\xbb\xbf':
            skip_utf8_seek = 3


    with open(filename, "r") as csvfile:

        # remove ut-8 bon sig
        csvfile.seek(skip_utf8_seek)

        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            
            # trim = r"(.*?)\?"
            # match = r"https://stockx.imgix.net/(.*?)\?"
            # image_url = ''.join(re.findall(trim,url))
            # image_filename = ''.join(re.findall(match,url))
            download_image(dest_dir, row)

def download_image(dest_dir, row):

    # image_url = fix_url(image_url)
    image_url = row['image-src']
    image_filename = row['image-name']
    try:

        fout = open("../stockxData/faultyUrl.csv","a")
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
                        return
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
                        return
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
                        return
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
                        return
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
                        return
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
                        return
                else:
                    logging.warning("unknown image content type: %s \n url: %s" % (content_type, image_url))
                    fout.write(image_url + '\n')
                    return
        else:
            logging.warning("unknown image content type: %s \n url: %s" % (content_type, image_url))
            fout.write(image_url + '\n')
            return
        
        image_path.replace(oldSuffix, newSuffix)
        # print (tmp_file_name, image_path)
        shutil.move(tmp_file_name, image_path)
        
    except Exception as e:
        logging.warning("Image download error. %s" % e)

def get_csv_image_dir(csv_filename):

    base = os.path.basename(csv_filename)
    dir = os.path.splitext(base)[0]

    if not os.path.exists(dir):
        os.makedirs(dir)

    return dir

def download_csv_file_images(filename):

    logging.info("importing data from %s" % filename)

    dest_dir = get_csv_image_dir(filename)

    download_csv_row_images(filename, dest_dir)

def main(args):

    # filename passde through args
    if len(args) >=2:
        csv_filename = args[1]
        download_csv_file_images(csv_filename)
        logging.info("image download completed")

    else:
        logging.warning("no input file found")

    time.sleep(20)

main(sys.argv)
# download_image('https://stockx.imgix.net/adidas-I-5923-Pride-Pack-2018.png', 'test', )