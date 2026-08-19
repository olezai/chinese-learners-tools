# HSK preparation tools
Usage:
Get a list of words by desired HSK level
python hsk_query.py -l 3 --export csv
python hsk_query.py -l 4 -v old --export csv -o hsk4_vocab.csv
python hsk_query.py -l 2 --inclusive -n 50 --export csv -o hsk2_top50.csv

Create input_characters.txt for handwriting practice:
py gen-practice-sheets.py

The output is a PDF that can be printed out.
