from collections import defaultdict,Counter
from itertools import islice
from pathlib import Path
import argparse
import sys, copy
import networkx as nx


from conll import CoNLLReader,DependencyTree


###TODO determine which mwes are free and which ones are fixed
###TODO newhead feature?

fixedmwes = None #"= ["mwe","name"]
freemwes = None #= ["compound:prt",'aux',"compound"]

def read_mwe_lists(infile):
    allmwe = [x.strip() for x in open(infile).readlines()]
    fixed_free_boundary = allmwe.index("---")
    #fixed,free
    return allmwe[:fixed_free_boundary],allmwe[fixed_free_boundary:]

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
            overall_mwe_function = sent[head_over_mwe][h]['deprel']
            #print(h,d,overall_mwe_function,sent)
            if overall_mwe_function.startswith('mwe_') or "_rmwe" in overall_mwe_function:
                pass
            else:
                sent[h][d]["deprel"] =  "mwe_"+most_common_label_filler[overall_mwe_function]
    return sent

def is_well_formed_span(span): #1,2,3 is good, 1,3 is not.
    span = sorted(list(span))
    span_max = max(span) + 1 #outer boundary of range
    span_min = min(span)
    if span == list(range(span_min,span_max)):
        return True
    else:
        return False

def modif_labels(sent):
    for h,d in sent.edges():
        if sent[h][d]["deprel"] == "mwe":
            sent[h][d]["deprel"] = "fixed"
            print(sent)
    return sent

def flatten_mwe_chains(sent,most_common_label_filler):
    auxgraph = nx.Graph()
    outsent = DependencyTree()
    outsent.add_nodes_from(sent.nodes(data=True))

    for h,d in sent.edges():
        if sent[h][d]["deprel"] in fixedmwes:
            auxgraph.add_edge(h,d,sent[h][d])

    #print(sent)
    #print(list(nx.connected_components(auxgraph)))

    for component in nx.connected_components(auxgraph):
        if is_well_formed_span(component): #if it is well-formed we can treat is as a fixed continuous MWE
            component = sorted(component)
            span_head = min(component) #the leftmost item
            external_head_of_span = sent.head_of(span_head)
            previous_heads_of_span = [sent.head_of(x) for x in component]
            potential_external_heads = sorted((set(previous_heads_of_span).difference(set(component))))

            #if len(potential_external_heads) == 0:
            #    print("COMPONENT",component,external_head_of_span)
            #    print(sent.deprel_sequence())
            #else:
            #    external_head = potential_external_heads[0]

            external_head = potential_external_heads[0]
            potential_internal_heads = sorted((set(sent[external_head].keys()).intersection(set(component))))
            internal_head = potential_internal_heads[0]
            overal_mwe_function = sent[external_head][internal_head]["deprel"]

            #Attach all members of the MWE to the lefmost token of the MWE
            for n in component[1:]:
                former_head_of_n = sent.head_of(n)
                former_label_of_n = sent[former_head_of_n][n]["deprel"]
                #mwe_label = former_label_of_n + "_rmwe_" + most_common_label_filler[former_label_of_n]
                mwe_label = former_label_of_n + "_"+most_common_label_filler[former_label_of_n]

                outsent.add_edge(component[0],n,{"deprel":mwe_label})
                #outsent.add_edge(component[0], n, {"deprel": 'nsubj'})

            #Attach the leftmost token of the MWE to the estimated original head
            outsent.add_edge(external_head,component[0], {"deprel": overal_mwe_function})
            #Attach all dependents of the component to the first word in the MWE

            external_dependents_of_mwe = []
            for x in component:
                external_dependents_of_mwe.extend([y for y in sent[x].keys() if y not in component])
                for ext_dep in external_dependents_of_mwe:
                    head_of_external_dependent = sent.head_of(ext_dep)
                    second_degree_dependent_label = sent[head_of_external_dependent][ext_dep]['deprel']
                    outsent.add_edge(component[0], ext_dep, {"deprel": second_degree_dependent_label})
                    #outsent.add_edge(component[0], ext_dep, {"deprel": 'nsubj'})

        else: #if the span is not well-formed, we treat is a non-fixed MWE
            pass

    # Complete the tree with the already-existing edges from sent
    # Check for well-formed ness, isTree, isDGA, etc.

    already_attached = [d for h, d in outsent.edges()]
    for h, d in sent.edges():
        if d not in already_attached:
            outsent.add_edge(h, d, {"deprel": sent[h][d]['deprel']})

    #for h,d, in outsent.edges():
    #    if type(outsent[h][d]['deprel']) != str:
    #        if (h,d) in sent.edges():
    #            outsent[h][d]['deprel']=sent[h][d]['deprel']
    #        else:
    #            print("new edge",h,d,outsent[h][d]['deprel'],sent)
    #
    #print(outsent.pos_sequence(),nx.is_tree(outsent))
    return outsent



def modif_free_mwe_labels(sent,most_common_label_filler):
    for h,d in sent.edges():
        if sent[h][d]["deprel"] in freemwes:
            head_over_mwe = sent.head_of(h)
            overall_mwe_function = sent[head_over_mwe][h]['deprel']
            if type(overall_mwe_function) == str:
                if "_" in overall_mwe_function or overall_mwe_function.startswith("mwe"):
                    pass
                else:
                    sent[h][d]["deprel"] = sent[h][d]["deprel"]+"_rmwe_"+most_common_label_filler[overall_mwe_function]
            else:
                #pass
                print("MUCHO WRONG",h,d,overall_mwe_function)
                print(sent, sent.edges(),nx.is_tree(sent))

    return sent

def detect_violations(sent):
    for h,d in sent.edges():
        #if sent[h][d]["deprel"].startswith("mwe_") and h > d:
        if str(sent[h][d]["deprel"]).startswith("mwe"):
            if h > d:
                sent[h][d]["deprel"] = sent[h][d]["deprel"]+"_SEQUENCEVIOLATION"
            else:
                sent[h][d]["deprel"] = sent[h][d]["deprel"] + "_SEQUENCEALRIGHT"
    return sent


def inspectlabels(milestone,sent):
    for h,d in sent.edges():
        if type(sent[h][d]['deprel']) == str:
            pass
        else:
            print(milestone,"ARLAMA",sent)
    if not nx.is_tree(sent):
        print("not tree")

def main():
    parser = argparse.ArgumentParser(description="""Convert conllu to conll format""")
    parser.add_argument('--trainfile', help="conllu file",default="/Users/hector/data/UD1.3/ud-treebanks-v1.3/UD_French/fr-ud-train.conllu")
    parser.add_argument('--input', help="conllu file",default="/Users/hector/data/UD1.3/ud-treebanks-v1.3/UD_French/fr-ud-dev.conllu")
    parser.add_argument('--output', default=Path("out.conll"),type=Path)
    parser.add_argument('--mwelists',default="multiwordlabels.txt")
    args = parser.parse_args()
    print(args.output,"LANGUAGE Starts here")

    global fixedmwes
    global freemwes
    if sys.version_info < (3,0):
        print("Sorry, requires Python 3.x.") #suggestion: install anaconda python
    fixedmwes,freemwes = read_mwe_lists(args.mwelists)
    print(fixedmwes,freemwes)
    cio = CoNLLReader()
    train_treebank = cio.read_conll_u(args.input)#, args.keep_fused_forms, args.lang, POSRANKPRECEDENCEDICT)
    most_common_label_filler = get_most_common_filler(train_treebank)

    orig_treebank = cio.read_conll_u(args.input)#, args.keep_fused_forms, args.lang, POSRANKPRECEDENCEDICT)
    modif_treebank =[]
    for s in orig_treebank:
        sx = modif_labels(s)
        s1 = flatten_mwe_chains(sx,most_common_label_filler)
        sm = modif_fixed_mwe_labels(s1,most_common_label_filler)
        #sm3 = detect_violations(sm2)
        modif_treebank.append(sm)

    print("LANGUAGE Finished here")
    cio.write_conll(modif_treebank,args.output, "conll2006",print_fused_forms=False, print_comments=False)

if __name__ == "__main__":
    main()