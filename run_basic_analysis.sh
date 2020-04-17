#!/bin/bash

#SBATCH -p largenode
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 6
#SBATCH --mem=256000
#SBATCH -t 72:00:00

#dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source ~/.bashrc

python ../tcr-dist/make_10x_clones_file.py -c $consensus -f $contig --organism $organism -o clones_file.tsv --clobber
python ../tcr-dist/run_basic_analysis.py --clones_file clones_file.tsv --organism human > analysis.log 2> analysis.err
python ../tcr-dist/get_clone_attributes.py --clones_file clones_file.tsv -o clones_attr.csv
python ../tcr-dist/join_cell_files.py clones_file.csv clones_attr.csv clones_file_attr.csv
python ../tcr-dist/join_cell_files.py clones_file_attr.csv kpca_clone_data.csv_UNK_E.csv clones_file_attr_pca.csv
python ../tcr-dist/match_clones_to_cells.py --clones_file clones_file_attr_pca.csv -o cell_attr_pca.csv
python ../tcr-dist/convert_categorical_data.py cell_attr_pca.csv
