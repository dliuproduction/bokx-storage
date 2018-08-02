import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from os import walk
import requests
import json
import csv

def uploadFiles(folder):
  files = []
  for (dirpath, dirnames, filenames) in walk(folder):
      files.extend(filenames)
      break

  count = open("uploadCount.csv", 'wb')
  wtr = csv.writer(count)
  for i in range(0, len(files)):
    # filename = 'adidas-3d-runner-black.jpg'
    url = 'https://firebasestorage.googleapis.com/v0/b/bokx-fa37d.appspot.com/o/shoes%2F+' + files[i]
    if 'jpg' in files[i] or 'jpeg' in files[i]:
      headers = {'Content-Type': 'image/jpg'}
    elif 'png' in files[i]:
      headers = {'Content-Type': 'image/png'}
    else:
      continue
    payload = open('../stockxData/result7/' + files[i], 'rb')
    r = requests.post(url, headers=headers, data=payload)
    if r.status_code == 200:
      print 'uploaded file: ' + str(i) + ' ' + files[i]
      wtr.writerow((str(i), 'success', files[i], str(r.status_code)))
    else: 
      print 'error uploading: ' + files[i] + ' status code: ' + str(r.status_code)
      wtr.writerow((str(i), 'fail', files[i], str(r.status_code)))
      continue

def uploadDatabase(src):

    # Use the application default credentials
  cred = credentials.ApplicationDefault()
  firebase_admin.initialize_app(cred, {
    'projectId': 'bokx-fa37d',
  })

  db = firestore.client()

  with open(src, "r") as source:
    csvreader = csv.reader(source, delimiter=',')
    csvreader.next()
    count = 0
    for row in csvreader:

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
        u'brand': unicode(brand),
        u'series': unicode(series),
        u'model': unicode(model),
        u'version': unicode(version),
        u'name': unicode(name),
        u'style': unicode(style),
        u'colorway': unicode(colorway),
        u'retail_price': unicode(retail_price),
        u'release_date': unicode(release_date),
        u'image_name': unicode(image_name),
        u'shoeid': {
          u'new':{
            '5': unicode(shoeid + '5N'),
            '6': unicode(shoeid + '6N'),
            '7': unicode(shoeid + '7N'),
            '7.5': unicode(shoeid + '7HN'),
            '8': unicode(shoeid + '8N'),
            '8.5': unicode(shoeid + '8HN'),
            '9': unicode(shoeid + '9N'),
            '9.5': unicode(shoeid + '9HN'),
            '10': unicode(shoeid + '10N'),
            '10.5': unicode(shoeid + '10HN'),
            '11': unicode(shoeid + '11N'),
            '11.5': unicode(shoeid + '11HN'),
            '12': unicode(shoeid + '12N'),
            '12.5': unicode(shoeid + '12HN'),
            '13': unicode(shoeid + '13N'),
            '14': unicode(shoeid + '14N'),
            '15': unicode(shoeid + '15N'),
            '16': unicode(shoeid + '16N')
          },
          u'used':{
            '5': unicode(shoeid + '5U'),
            '6': unicode(shoeid + '6U'),
            '7': unicode(shoeid + '7U'),
            '7.5': unicode(shoeid + '7HU'),
            '8': unicode(shoeid + '8U'),
            '8.5': unicode(shoeid + '8HU'),
            '9': unicode(shoeid + '9U'),
            '9.5': unicode(shoeid + '9HU'),
            '10': unicode(shoeid + '10U'),
            '10.5': unicode(shoeid + '10HU'),
            '11': unicode(shoeid + '11U'),
            '11.5': unicode(shoeid + '11HU'),
            '12': unicode(shoeid + '12U'),
            '12.5': unicode(shoeid + '12HU'),
            '13': unicode(shoeid + '13U'),
            '14': unicode(shoeid + '14U'),
            '15': unicode(shoeid + '15U'),
            '16': unicode(shoeid + '16U')
          }
        }
      }

      if brand == 'null':
        doc_ref = db.collection(u'brand').document(u'null') \
        .collection(u'name').document(name)
      else:
        if series == 'null':
          doc_ref = db.collection(u'brand').document(brand) \
          .collection(u'series').document(u'null') \
          .collection(u'name').document(name)
        else:
          if model == 'null':
            doc_ref = db.collection(u'brand').document(brand) \
            .collection(u'series').document(series) \
            .collection(u'model').document(u'null') \
            .collection(u'name').document(name)
          else:
            if version == 'null':
              doc_ref = db.collection(u'brand').document(brand) \
              .collection(u'series').document(series) \
              .collection(u'model').document(model) \
              .collection(u'version').document(u'null') \
              .collection(u'name').document(name)
            else:
              doc_ref = db.collection(u'brand').document(brand) \
              .collection(u'series').document(series) \
              .collection(u'model').document(model) \
              .collection(u'version').document(version) \
              .collection(u'name').document(name)

      doc_ref.set(data)

      count = count + 1
      print 'uploaded shoe data: #', count, ' ', name

uploadDatabase('../stockxData/result10.csv')
# uploadFiles('result9/')