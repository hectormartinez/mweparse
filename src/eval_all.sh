for variant in v0 va vb vc
do
for lang in ar bg ca da de es_ancora en fa "fi_ftb" fr id it lv nl_lassysmall pt_br ro ru_syntagrus sl sv tr
do
for parser in F B
do
filename=/Users/hector/Downloads/mweparsepreds/$lang"_dev_"$variant".conll."$variant"-"$parser".conll"
python evalmweparse.py --predictedfile $filename --mwelists $variant".txt"
done
filename=/Users/hector/Downloads/mweparsepreds/$lang"_dev_"$variant".conll."$variant".conll"
python evalmweparse.py --predictedfile $filename --mwelists $variant".txt"

done
done