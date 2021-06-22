#!/bin/bash

#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 6
#SBATCH --mem=256000
#SBATCH -t 150:00:00

while [ ! -z $1 ]; do if [ ${1:0:1} == - ]; then declare ${1//-/}=$2; shift; fi; shift; done

if [ -f ERROR.err ]; then
  rm ERROR.err
fi

if [ -d processing ]; then
  rm -r processing
fi

help() {
  echo this is the helper script for running tcr-dist on 10x and bd data.
  echo usage:
  echo    sbatch ../tcr-dist/run_basic_analysis_new.sh --type 10x --consensus consensus_annotations.csv --contig contig_annotations.csv --organism human
  echo or sbatch ../tcr-dist/run_basic_analysis_new.sh --type bd --percell _3_EXP1-mRNA-ST-TCR_VDJ_perCell.csv --organism human
  echo in case of errors, a file called ERROR.err will be created.
  echo check the slurm_xxxxx.out file for log messages
}

#dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
dir=/fh/fast/newell_e/Nicholas/Tcr_scripts/tcr-dist
echo directory of script: $dir

SAVE_PATH="$PATH"
export PATH="$dir/../miniconda/miniconda/bin:$PATH"


if [ -z $type ]; then
  if [ -z $percell ]; then
    type=10x
  else
    type=bd
  fi
fi

mkdir processing
cd processing

if [ $type == bd ]; then
  if ! [ -f "../$percell" ]; then
      echo "file '$percell' does not exist"
      echo "file '$percell' does not exist" > ../ERROR.err
      help
  		exit 1
  fi
fi

if [ $type == 10x ]; then
  if ! [ -f "../$consensus" ]; then
      echo "file '$consensus' does not exist"
      echo "file '$consensus' does not exist" > ../ERROR.err
      help
  		exit 1
  fi
  if ! [ -f "../$contig" ]; then
      echo "file '$contig' does not exist"
      echo "file '$contig' does not exist" > ../ERROR.err
      help
  		exit 1
  fi
fi


if [ $type == 10x ]; then
  python $dir/make_10x_clones_file.py -c ../$consensus -f ../$contig --organism $organism -o clones_file.tsv --clobber > make_10x_clones_file.log 2> make_10x_clones_file.err
fi
if [ $type == bd ]; then
  python $dir/make_cell_file_bd.py ../$percell cell_file.csv > make_cell_file_bd2.log 2> make_cell_file_bd2.err
  python $dir/make_clones_file.py cell_file.csv clones_file_unconverted.tsv > make_clones_file.log 2> make_clones_file.err
  python $dir/file_converter.py --input_format clones --output_format clones --input_file clones_file_unconverted.tsv --output_file clones_file.tsv --organism human --clobber --epitope UNK_E --check_genes > file_converter.log
fi
python $dir/run_tcr_to_pca.py --clones_file clones_file.tsv --organism human -o kpca_clone_data.csv > analysis.log 2> analysis.err
python $dir/get_clone_attributes.py --clones_file clones_file.tsv -o clones_attr.csv > get_clone_attr.log 2> get_clone_attr.err
python $dir/csvfile.py join-row clones_attr.csv clones_file.tsv kpca_clone_data.csv clone_output_data.csv > join_files.log 2> join_files.err
python $dir/match_clones_to_cells2.py --clones_file clone_output_data.csv -o ../cell_output_data.csv > match_clones_to_cells.log 2> match_clones_to_cells.err
python $dir/csvfile.py convert ../cell_output_data.csv ../cell_output_data.fcs > convert_files.log 2> convert_files.err

export PATH="$SAVE_PATH"
echo $PATH

mkdir log
mkdir err
mv *.log log/
mv *.err err/


if [ -z "$(grep Traceback err/*)" ]; then
	echo SUCESS: completed without errors
else
	echo ERR: errors detected
	echo ERR: check processing/err/ for error logs
	echo ERR: errors detected, check processing/err/ for error logs > ../ERROR.err
fi
