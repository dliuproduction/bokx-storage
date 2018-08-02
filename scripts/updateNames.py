from os import walk
import csv

def updateNames(folder, res):
  with open(res, 'wb') as result:
    wtr = csv.writer(result)
    for (dirpath, dirs, files) in walk(folder):
      count = 0
      for file in sorted(files): 
        wtr.writerow([str(file)])
        count = count + 1
        print 'count: ' + str(count) + ' updating name : ' + file

# updateNames('../stockxData/result7', '../stockxData/updatedNames.csv')
with open('../stockxData/result9.csv', 'rb') as source:
  rdr = csv.reader(source, delimiter=',')
  with open('../stockxData/result10.csv', 'wb') as result:
    wtr = csv.writer(result, delimiter=',')
    for r in rdr:
      wtr.writerow(r)