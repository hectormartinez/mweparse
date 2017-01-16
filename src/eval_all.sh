for variant in v0 va vb vc
do
for lang in ar bg ca da de es en fa "fi_ftb" fr id it lv nl_lassysmall pt_br ro ru_syntagrus sl sv tr
do
filename=/Users/hector/Downloads/mweparsepreds/$lang"_dev_"$variant".conll."$variant"-B.conll"
python evalmweparse.py --predictedfile $filename --mwelists $variant".txt"
filename=/Users/hector/Downloads/mweparsepreds/$lang"_dev_"$variant".conll."$variant".conll"
python evalmweparse.py --predictedfile $filename --mwelists $variant".txt"
done
done