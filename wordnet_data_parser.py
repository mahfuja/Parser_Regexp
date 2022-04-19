import sys
import re
file_ = open(sys.argv[1], 'r').read()

#logRegex = "^ <synset id=\"(.*)\".ofs=.*\n..<terms>[\s\S]*?<\/terms>\n..<keys>[\s\S]*?<\/keys>\n..<gloss desc=\"orig\">\n...<orig>(.*)<\/orig>"
logRegex = "^ <synset id=\"(.*)\".ofs=.*\n..<terms>\n...<term>(.*)<\/term>[\s\S]*?<\/terms>\n..<keys>[\s\S]*?<\/keys>\n..<gloss desc=\"orig\">\n...<orig>(.*)<\/orig>"
entity2text_all = {}
entity2name_all = {}

match = re.findall(logRegex,file_, re.M)
for i in range(0,len(match)):
    desc = re.sub("[\"]", "\\\"", match[i][2])
    entity2text_all[match[i][0]] = "\""+desc+"\"@en"
    entity2name_all[match[i][0]] = match[i][1]

entity2text = {}
entity2name = {}

to_read_ent = open('ent2id', 'r')
for line in to_read_ent.readlines():
    ent, txt = line.strip().split('\t')
    if ent not in entity2text_all.keys():
        continue
    entity2text[ent] = entity2text_all[ent]
    entity2name[ent] = entity2name_all[ent]
to_read_ent.close()

for (dic, f) in zip([entity2text, entity2name], ['description.txt', 'entities.dict']):
    ff = open(f, 'w+')
    for (x, i) in dic.items():
        ff.write("{}\t{}\n".format(x, i))
    ff.close()
