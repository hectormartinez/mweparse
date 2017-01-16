import argparse
from ud2mweconll import read_mwe_lists
import sys
from conll import CoNLLReader,DependencyTree
from collections import Counter
from decimal import *
getcontext().prec = 2

fixedmwes = None
freemwes = None
#all except PUNCT
validpos = "ADJ ADP ADV AUX CONJ DET INTJ NOUN NUM PART PRON PROPN SCONJ SYM VERB X".split(" ")
nominalrelations = "nsubj dobj nmod".split()
rootrelations = "root".split()

def formatlabel(x):
    return x.split("_")[0]

def perfect_match_UAS(predtree,goldtree):
    for edge in goldtree.edges():
        if edge not in predtree.edges():
            return 0
    return 1

def perfect_match_LAS(predtree,goldtree):
    for (h,d) in goldtree.edges():
        if (h,d) not in predtree.edges():
            return 0
        if predtree[h][d]["deprel"] != goldtree[h][d]["deprel"]:
            return 0
    return 1

def LAS(predtree,goldtree,validpos):
    matches = 0
    inter = set(goldtree.edges()).intersection(set(predtree.edges()))
    validnodes = get_valid_pos_nodes(goldtree,validpos)
    tokens = len(validnodes)
    for (h, d) in inter:
        if d in validnodes and goldtree[h][d]["deprel"] == predtree[h][d]["deprel"] :
            matches += 1
    return matches, tokens


def LAS_labels(predtree,goldtree,acceptedlabels):
    matches = 0
    tokens = 0
    inter=set(goldtree.edges()).intersection(set(predtree.edges()))
    validnodes = get_valid_label_nodes(goldtree,acceptedlabels)
    tokens = len(validnodes)
    for h,d in inter:
        if d in validnodes:
            if predtree[h][d]["deprel"] == goldtree[h][d]["deprel"]:
                matches += 1
    return matches, tokens

def get_valid_pos_nodes(goldtree,validpos):
    validnodes = []
    for n in goldtree.nodes():
        if goldtree.node[n]["cpostag"] in validpos:
            validnodes.append(n)
    return validnodes

def get_valid_label_nodes(goldtree,validlabels):
    validnodes = []
    for h,d in goldtree.edges():
        if goldtree[h][d]["deprel"] in validlabels:
            validnodes.append(d)
    return validnodes

def UAS(predtree,goldtree,validpos):
    matches = 0
    inter = set(goldtree.edges()).intersection(set(predtree.edges()))
    validnodes = get_valid_pos_nodes(goldtree,validpos)
    tokens = len(validnodes)
    for (h, d) in inter:
        if d in validnodes:
            matches += 1
    return matches, tokens


def remove_punctuations(tree):
    return tree


def report_metrics(predictedfile,metrics):
    #every metric that begins with n is a numerator
    #with a denominator that begins with d
    o = dict()
    outname = predictedfile.split("/")[-1]
    outname = outname.replace("_dev_","\t").replace(".conll.","").replace(".conll","")
    outname = outname.replace("v0v0","v0").replace("vava","va").replace("vbvb","vb").replace("vcvc","vc")
    o["z_perfect_UAS"] = metrics["n_perfect_match_UAS"] / metrics["d_sentences"]
    o["z_perfect_LAS"] = metrics["n_perfect_match_LAS"] / metrics["d_sentences"]
    o["a__LAS"] = metrics["n_LAS"] / metrics["d_words"]
    o["a_UAS"] = metrics["n_UAS"] / metrics["d_words"]
    o["b_fixed_LAS"] = metrics["n_fixed_LAS"] / metrics["d_n_fixedtokens"]
    o["b_free_LAS"] = metrics["n_free_LAS"] / metrics["d_n_freetokens"]
    o["b_nominal_LAS"] = metrics["n_nominal_LAS"] / metrics["d_n_nominaltokens"]
    o["boot_LAS"] = metrics["n_root_LAS"] / metrics["d_n_roottokens"]

    #print(sorted(o.keys()))
    print("\t".join([outname]+["{0:.2f}".format(o[k]) for k in sorted(o.keys())]))



def read_trees(infile):
    predicted = []
    gold = []
    fields = "idx form lemma cpostag postag feats phead plabel ghead glabel".split()
    worddicts = []
    for line in open(infile).readlines():
        line = line.strip()
        if line:
            wdict = dict([[x,y] for x,y in zip(fields,line.strip().split("\t"))])
            worddicts.append(wdict)
        else:
            predtree = DependencyTree()
            goldtree = DependencyTree()
            goldtree.add_node(0,{'form':"", 'cpostag' : 'ROOT'})
            for currentword in worddicts:
                token_dict = dict([(x, currentword[x]) for x in fields[1:7]])
                goldtree.add_node(int(currentword['idx']),token_dict)
                #print(token_dict)
            predtree.add_nodes_from(goldtree)
            for cw in worddicts:
                goldtree.add_edge(int(cw['ghead']),int(cw['idx']),{'deprel':formatlabel(cw['glabel'])})
                predtree.add_edge(int(cw['phead']),int(cw['idx']), {'deprel': formatlabel(cw['plabel'])})
            worddicts = []
            predicted.append(predtree)
            gold.append(goldtree)
    return predicted,gold



def main():
    parser = argparse.ArgumentParser(description="""Convert conllu to conll format""")
    parser.add_argument('--predictedfile', help="conllu file",default="/Users/hector/Downloads/mweparsepreds/en_dev_va.conll.va.conll")
    parser.add_argument('--mwelists',default="vb.txt")
    args = parser.parse_args()

    global fixedmwes
    global freemwes
    if sys.version_info < (3,0):
        print("Sorry, requires Python 3.x.") #suggestion: install anaconda python
    fixedmwes,freemwes = read_mwe_lists(args.mwelists)
    predictedtrees,goldtrees = read_trees(args.predictedfile)
    metrics = Counter()
    metrics["d_sentences"] = len(goldtrees)
    for p,g in zip(predictedtrees,goldtrees):
        metrics["n_perfect_match_UAS"] += perfect_match_UAS(p,g)
        metrics["n_perfect_match_LAS"] += perfect_match_LAS(p, g)

        matches,tokens = UAS(p, g,validpos)
        metrics["n_UAS"] += matches
        metrics["d_words"] += tokens


        matches,tokens = LAS(p, g,validpos)
        metrics["n_LAS"] += matches

        matches, tokens = LAS_labels(p, g,fixedmwes)
        metrics["n_fixed_LAS"] += matches
        metrics["d_n_fixedtokens"] += tokens

        matches, tokens = LAS_labels(p, g, freemwes)
        metrics["n_free_LAS"] += matches
        metrics["d_n_freetokens"] += tokens

        matches, tokens = LAS_labels(p, g, nominalrelations)
        metrics["n_nominal_LAS"] += matches
        metrics["d_n_nominaltokens"] += tokens

        matches, tokens = LAS_labels(p, g, rootrelations)
        metrics["n_root_LAS"] += matches
        metrics["d_n_roottokens"] += tokens


    for k in metrics:
        if metrics[k] == 0:
            metrics[k] = 1 #avoid division by zero

    report_metrics(args.predictedfile,metrics)
if __name__ == "__main__":
    main()