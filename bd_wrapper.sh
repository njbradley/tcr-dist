#!/bin/bash

#SBATCH -p largenode
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 6
#SBATCH --mem=256000
#SBATCH -t 48:00:00

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source ~/.bashrc

python $dir/make_cell_file_bd.py $1 clones_file.csv
python $dir/make_cell_file_bd.py $1 cell_file.tsv
python $dir/file_converter.py --input_format clones --output_format clones --input_file cell_file.tsv --output_file clones_file.tsv --organism human --clobber --epitope UNK_E --check_genes > file_converter.log
python $dir/run_tcr_to_pca.py --clones_file clones_file.tsv --organism human -o kpca_clone_data.csv > analysis.log 2> analysis.err
python $dir/get_clone_attributes.py --clones_file clones_file.tsv -o clones_attr.csv
python $dir/join_cell_files.py clones_file.csv clones_attr.csv clones_file_attr.csv
python $dir/join_cell_files.py clones_file_attr.csv kpca_clone_data.csv clones_kpca_data.csv
python $dir/join_cell_files.py clones_kpca_data.csv $1 all_cell_data.csv
python $dir/convert_categorical_data.py all_cell_data.csv