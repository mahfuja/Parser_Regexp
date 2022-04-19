#!/usr/bin/python

import sys
import re

file_ = open(sys.argv[1], 'r').read()
FO = open('output_file.txt', 'w')
FA = open('output_text.txt', 'w')

#logRegex = "^ <synset id=\"(.*)\".ofs=.*\n..<terms>[\s\S]*?<\/terms>\n..<keys>[\s\S]*?<\/keys>\n..<gloss desc=\"orig\">\n...<orig>(.*)<\/orig>"
logRegex = "^ <synset id=\"(.*)\".ofs=.*\n..<terms>\n...<term>(.*)<\/term>[\s\S]*?<\/terms>\n..<keys>[\s\S]*?<\/keys>\n..<gloss desc=\"orig\">\n...<orig>(.*)<\/orig>"
data = []
data1 = []

def dataParsing(file_,data):
    match = re.findall(logRegex,file_, re.M)
    print(len(match))
    for i in range(0,len(match)):
        st = re.sub("[\"]", "\\\"", match[i][2])
        FO.write("%s\t\"%s\"@en\n" %(match[i][0],st))
        FA.write("%s\t%s\n" %(match[i][0],match[i][1]))
				
dataParsing(file_,data)

FO.close()
file1 = open('entity2id.txt','r')
file2 = open('output_file.txt', 'r')
FINAL = open('WN9_eid2description.txt', 'w')

file3 = open('output_text.txt', 'r')
FINAL2 = open('eid2text.txt', 'w')
for line in file1:
    l = line.split("\t")
    data1.append(l[0])
datafile = file2.readlines()
count = 0
for line in datafile:
    entity = line.split("\t")
    if entity[0] in data1:
        FINAL.write("%s" %(line))
        count = count+1
FINAL.close()
file1.close()
file2.close()

textfile = file3.readlines()
count = 0
for line in textfile:
        entity = line.split("\t")
        if entity[0] in data1:
                FINAL2.write("%s" %(line))
                count = count+1
file3.close()
FINAL2.close()



