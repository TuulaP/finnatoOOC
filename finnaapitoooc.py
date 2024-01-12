#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import csv
from pymarc import parse_xml_to_array, record_to_xml
import re


recordurl = "https://api.finna.fi/v1/record?id="
full = "&field[]=fullRecord"
suffix = "&field[]=id"
sample = "fikka.3741472"

uri  = recordurl + "fikka.3741472" + "&prettyPrint=false&lng=fi"

import urllib
import json
from pymarc import MARCReader
from io import BytesIO


def getFinnaRecord(bookid):

    print("GetFinnaRecord: ", recordurl+bookid+full)

    result = urllib.request.urlopen(recordurl+bookid+full).read()
    result = json.loads(result)
    result = result.get('records')

    print(result)
    print(">>", bookid, "\n")

    xmlmarc = result[0]['fullRecord']

    print(xmlmarc)

    # don't ask, this works.
    # for some reson pymarc likes to operate via file
    # even chatgpt couldn't figure out better  way,  it lies

    with open("kirja.xml", "wb") as text_file:
        text_file.write(xmlmarc.encode("UTF-8"))

    
    reader = parse_xml_to_array("kirja.xml")

    print(">>", xmlmarc)
    details={}
    details['fikkaid']=bookid


    for record in reader:
        print(record.as_dict())
        # Extract information from each record
        
        print('Author:', record.author())
        print('Publication Year:', record.pubyear())
        #print('ISBN:', record.isbn())


        details['title']= re.sub('\s*\/\s*$','',record.title())
        
        #"/"+record['100']['d'].replace(",","")+"/"+record['100']['0']   #record.author()
        details['author']=re.sub('\W*$','',record['100']['a'])
        details['authorid'] = record['100']['0'] #asteriid
        details['id']=record['015']['a']
        details['isbn']=record.isbn()
        details['year']=record.pubyear().replace("[","").replace("]","")
        details['language']= record['041']['a']
        details['publisher'] = re.sub('\W*$','',record.publisher())

    print("Chosen work: {0}, {1}".format(details['isbn'], details['title'].encode('utf-8')))
    #print(details)
    

    return details




# Get book data.

recorddata= getFinnaRecord(sample)

data=[]
data.append(recorddata)

# Bulk import fields
# Type	Internal Reference	Category of Work	Operating Platform	
# Title	Author or Performer Name 1	Author or Performer ID 1	Rights Holder Name 1	Rights Holder ID 1	
# Title ID	Language	Description	Alternative Title	
# Publisher/Producer/Broadcaster	Production/Publication/Broadcast Country	Production/Publication/Broadcast Date	Production/Publication/Broadcast Language	ISN type	ISN	Permalink	Thumbnail Link



# Create and  write temp csv.
with open('data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Write data.
    row = []
    for item in data:

        row.append('INDIVIDUAL')
        row.append(item['id'])
        row.append('LITERARY')
        row.append("")
        row.append(item['title'])
        row.append(item['author'])
        row.append(item['authorid'])  # should be viafid
        row.append("")
        row.append("")
        for _ in range(57):
            row.append("")  #57 fields in between
        row.append(item['language'])
        row.append("")
        row.append("")
        row.append(item['publisher'])

        writer.writerow(row)



print("done")
