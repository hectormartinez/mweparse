basepath=/Users/hector/data/UD1.3/ud-treebanks-v1.3
for section in dev test train
do
    for variant in ve #vd va vb vc #v0
    do
        for treebank in UD_French/fr UD_English/en UD_German/de UD_Finnish-FTB/fi_ftb UD_Swedish/sv UD_Russian/ru \
UD_Arabic/ar UD_Bulgarian/bg UD_Catalan/ca UD_Czech/cs UD_Danish/da UD_Dutch-LassySmall/nl_lassysmall UD_Indonesian/id \
UD_Italian/it UD_Latvian/lv UD_Persian/fa UD_Portuguese-BR/pt_br UD_Romanian/ro UD_Russian-SynTagRus/ru_syntagrus UD_Slovenian/sl \
UD_Spanish-AnCora/es_ancora UD_Turkish/tr
        do
        array=(${treebank//\// })
        lang=${array[1]}
        python ud2mweconll_strict.py --mwelists $variant.txt --output devsections/"$lang"_"$section"_"$variant".strict.conll --trainfile $basepath/$treebank-ud-train.conllu --input $basepath/$treebank-ud-$section.conllu
        done
    done
done