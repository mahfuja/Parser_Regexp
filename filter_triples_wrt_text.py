# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
import pkg_resources
import os
import errno
from pathlib import Path
import pickle
import numpy as np
import string
from re import sub
import torch
translator = str.maketrans('','', sub('\-', '', string.punctuation))
files = ['train', 'valid', 'test']
entities, relations, description, images, words = set(), set(), set(), set(), set()
for f in files:
    to_read = open(f+'.txt', 'r')
    for line in to_read.readlines():
        lhs, rel, rhs = line.strip().split('\t')
        entities.add(lhs)
        entities.add(rhs)
        relations.add(rel)
    to_read.close()
entities_to_id = {x: i for (i, x) in enumerate(sorted(entities))}
relations_to_id = {x: i for (i, x) in enumerate(sorted(relations))}
#####
n_relations = len(relations)
n_entities = len(entities)

id_to_texts = [0] * n_entities
id2txt = {}
all_sentences = [0] * n_entities
missing = []
id2texts = {}
to_read_text = open('description.txt', 'r')
for line in to_read_text.readlines():
    ent, txt = line.strip().split('\t')
    if ent not in entities_to_id.keys():
        continue
    description.add(txt)
    txt = txt.translate(translator).lower()
    id2txt[entities_to_id[ent]] =  txt

to_read_text.close()

#give id to all description
desc_to_id = {x: i for (i, x) in enumerate(sorted(description))}

# write ent to id / rel to id
for (dic, f) in zip([entities_to_id, relations_to_id, desc_to_id], ['ent2id', 'rel2id', 'desc2id']):
    ff = open(f, 'w+')
    for (x, i) in dic.items():
        ff.write("{}\t{}\n".format(x, i))
    ff.close()

for (ent, id) in entities_to_id.items():
    if id not in id2txt.keys():
       missing.append(ent)
print(n_entities)
print(len(missing))

for f in files:
    to_read = open(f+'.txt', 'r')
    examples = []
    for line in to_read.readlines():
        lhs, rel, rhs = line.strip().split('\t')
        if (lhs not in missing) and (rhs not in missing):
            examples.append([lhs, rel, rhs])

    ff = open(f+'_modified.txt', 'w+')
    for i in range(len(examples)):
        ff.write("{}\t{}\t{}\n".format(examples[i][0], examples[i][1], examples[i][2]))
    ff.close()
