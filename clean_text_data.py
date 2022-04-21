import numpy as np
import os
import re
all_sentences = {}
logRegex = "\(.*\)"
to_read_text = open('description.txt', 'r')
for line in to_read_text.readlines():
    ent, txt = line.strip().split('\t')
    no = re.sub("\(.*\)","",txt)
    no = re.sub("\[.*\]","",no)
    no = re.sub("\/.*\/","",no)
    all_sentences[ent]=no
for (dic, f) in zip([all_sentences], ['desc_new']):
    ff = open(f, 'w+')
    for (x, i) in dic.items():
        ff.write("{}\t{}\n".format(x, i))
    ff.close()
