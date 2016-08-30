from collections import defaultdict,Counter
from itertools import islice
from pathlib import Path
import argparse
import sys, copy
import networkx as nx


from conll import CoNLLReader,DependencyTree


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

def is_well_formed_span(span): #1,2,3 is good, 1,3 is not.
    span = sorted(list(span))
    span_max = max(span) + 1 #outer boundary of range
    span_min = min(span)
    if span == list(range(span_min,span_max)):
        return True
    else:
        return False

def flatten_mwe_chains(sent,most_common_label_filler):
    auxgraph = nx.Graph()
    outsent = DependencyTree()
    outsent.add_nodes_from(sent.nodes())
    for h,d in sent.edges():
        if sent[h][d]["deprel"] in fixedmwes:
            auxgraph.add_edge(h,d,sent[h][d])
    for component in nx.connected_components(auxgraph):
        if is_well_formed_span(component): #if it is well-formed we can treat is as a fixed continuous MWE
            component = sorted(component)
            span_head = min(component) #the leftmost item
            external_head_of_span = sent.head_of(span_head)
            previous_heads_of_span = [sent.head_of(x) for x in component]
            potential_external_heads = sorted((set(previous_heads_of_span).difference(set(component))))
            external_head = potential_external_heads[0]
            potential_internal_heads = sorted((set(sent[external_head].keys()).intersection(set(component))))
            internal_head = potential_internal_heads[0]
            overal_mwe_function = sent[external_head][internal_head]["deprel"]

            #Attach all members of the MWE to the lefmost token of the MWE
            for n in component[1:]:
                former_head_of_n = sent.head_of(n)
                former_label_of_n = sent[former_head_of_n][n]["deprel"]
                mwe_label = former_label_of_n + "_rmwe_" + most_common_label_filler[former_label_of_n]
                outsent.add_edge(component[0],n,{"deprel":mwe_label})
            #Attach the leftmost token of the MWE to the estimated original head
            outsent.add_edge(external_head,component[0], {"deprel": overal_mwe_function})
            #Attach all dependents of the component to the first word in the MWE
            external_dependents_of_mwe = []
            for x in component:
                external_dependents_of_mwe.extend([y for y in sent[x].keys() if y not in component])
                for ext_dep in external_dependents_of_mwe:
                    head_of_external_dependent = sent.head_of(ext_dep)
                    second_degree_dependent_label = sent[head_of_external_dependent]
                    outsent.add_edge(component[0], ext_dep, {"deprel": second_degree_dependent_label})

            #Complete the tree with the already-existing edges from sent
            already_attached = []
            for h,d in outsent.edges():
                already_attached.append(d)
            for h,d in sent.edges():
                if d not in already_attached:
                    outsent.add_edge(h,d,sent[h][d])

            #Check for well-formed ness, isTree, isDGA, etc.
        else: #otherwise we treat is a non-fixed MWE
            pass
    #
    print(outsent.edges(),nx.is_tree(outsent))



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
        flatten_mwe_chains(s,most_common_label_filler)
        sm = modif_fixed_mwe_labels(s,most_common_label_filler)
        sm2 = modif_free_mwe_labels(sm,most_common_label_filler)
        modif_treebank.append(sm2)

    cio.write_conll(modif_treebank,args.output, "conll2006",print_fused_forms=False, print_comments=False)

if __name__ == "__main__":
    main()