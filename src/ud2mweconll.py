from collections import defaultdict,Counter
from itertools import islice
from pathlib import Path
import argparse
import sys, copy

from conll import CoNLLReader


###TODO determine which mwes are free and which ones are fixed
###TODO newhead feature?

fixedmwes = ["mwe","compound",'name']
freemwes= ["compound:prt"]


def get_most_common_filler(treebank):
    labelcounters = defaultdict(Counter)
    outdict = {}
    for s in treebank:
        for h,d in s.edges():
            label = s[h][d]["deprel"]
            dep_pos = s.node[d]['cpostag']
            labelcounters[label][dep_pos]+=1
    for l in labelcounters.keys():
        outdict[l]=labelcounters[l].most_common(1)[0][0]
    return outdict

def get_POS_for_fixed_mwe(label):
    return label[::-1]

def modif_fixed_mwe_labels(sent,most_common_label_filler):
    for h,d in sent.edges():
        if sent[h][d]["deprel"] in fixedmwes:
            head_over_mwe = sent.head_of(h)
            overal_mwe_function = sent[head_over_mwe][h]['deprel']
            sent[h][d]["deprel"] = "mwe_"+most_common_label_filler[overal_mwe_function]
    return sent


def modif_free_mwe_labels(sent,most_common_label_filler):
    for h,d in sent.edges():
        if sent[h][d]["deprel"] in freemwes:
            head_over_mwe = sent.head_of(h)
            overal_mwe_function = sent[head_over_mwe][h]['deprel']
            sent[h][d]["deprel"] = sent[h][d]["deprel"]+"_rmwe_"+most_common_label_filler[overal_mwe_function]
    return sent


def main():
    parser = argparse.ArgumentParser(description="""Convert conllu to conll format""")
    parser.add_argument('--trainfile', help="conllu file",default="/Users/hmartine/data/UD1.3/ud-treebanks-v1.3/UD_English/en-ud-train.conllu")
    parser.add_argument('--input', help="conllu file",default="/Users/hmartine/data/UD1.3/ud-treebanks-v1.3/UD_English/en-ud-dev.conllu")
    parser.add_argument('--output', default=Path("out.conll"))


    args = parser.parse_args()

    if sys.version_info < (3,0):
        print("Sorry, requires Python 3.x.") #suggestion: install anaconda python
    cio = CoNLLReader()
    train_treebank = cio.read_conll_u(args.input)#, args.keep_fused_forms, args.lang, POSRANKPRECEDENCEDICT)
    most_common_label_filler = get_most_common_filler(train_treebank)

    orig_treebank = cio.read_conll_u(args.input)#, args.keep_fused_forms, args.lang, POSRANKPRECEDENCEDICT)
    modif_treebank =[]
    for s in orig_treebank:
        sm = modif_fixed_mwe_labels(s,most_common_label_filler)
        sm2 = modif_free_mwe_labels(sm,most_common_label_filler)
        modif_treebank.append(sm2)

    cio.write_conll(modif_treebank,args.output, "conll2006",print_fused_forms=False, print_comments=False)

if __name__ == "__main__":
    main()