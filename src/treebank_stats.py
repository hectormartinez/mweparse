from collections import defaultdict,Counter
from itertools import islice
from pathlib import Path
import argparse
import sys, copy
import networkx as nx


from conll import CoNLLReader,DependencyTree


###TODO determine which mwes are free and which ones are fixed
###TODO newhead feature?




def main():
    parser = argparse.ArgumentParser(description="""Convert conllu to conll format""")
    parser.add_argument('--input', help="conllu file",default="/Users/hector/data/UD1.3/ud-treebanks-v1.3/UD_English/en-ud-test.conllu")



    args = parser.parse_args()

    if sys.version_info < (3,0):
        print("Sorry, requires Python 3.x.") #suggestion: install anaconda python
    cio = CoNLLReader()


    orig_treebank = cio.read_conll_u(args.input)#, args.keep_fused_forms, args.lang, POSRANKPRECEDENCEDICT)
    modif_treebank =[]
    labelcounter = Counter()
    for s in orig_treebank:
        labelcounter.update(s.deprel_sequence())
    print(labelcounter)


if __name__ == "__main__":
    main()