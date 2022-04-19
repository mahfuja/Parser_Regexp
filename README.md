# Parser_Regexp

# wordnet_data_parser.py extracts entity name, description for all synset  id of wordnet data.

The source is from:  https://wordnetcode.princeton.edu/glosstag-files/WordNet-3.0-glosstag/WordNet-3.0/glosstag/merged/noun.xml

command: python wordnet_data_parser.py noun.xml[input file]

input file: ent2id[contains synset id with ID], noun.xml

output: 'entities.dict' contains synset id and entity name, 'description.txt' contains synset id and entity description

# LogParser.py extracts data from log file by using regular expression.

command: python LogParser.py inputfile outputfile
