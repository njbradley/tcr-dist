import matplotlib
import numpy
import scipy
import time
import os
import subprocess
import sys
from paths import path_to_scripts, path_to_tablesorter_files
from basic import *

with Parser(locals()) as p:
    p.str('clones_file')
    p.str('organism').required()
    p.str('distance_params')
    p.str('output_file').shorthand('o').required()
    p.flag('force')
    p.flag('dry_run')
    p.flag('intrasubject_nbrdists').described_as('Include TCRs from the same subject when computing the nbrdist (aka NNdistance) score')
    p.set_help_prefix("""
                      """)

print ''

if distance_params:
    distance_params_args = ' --distance_params {} '.format( distance_params )
else:
    distance_params_args = ' '


def run(command):
    print command
    if not dry_run:
        os.system(command)
    print ''


## compute distances
distfiles = glob('{}_*.dist'.format(clones_file[:-4]))

cmd = 'python {}/compute_distances.py {} {} --organism {} --clones_file {} > {}_cd.log 2> {}_cd.err'\
    .format( path_to_scripts, distance_params_args, ' --intrasubject_nbrdists '*intrasubject_nbrdists,
             organism, clones_file, clones_file, clones_file )
if force or not distfiles: run(cmd)

## make kpca landscape plots
kpca_clone_data_file = output_file

cmd = 'python {}/make_kpca_plots.py --organism {} --clones_file {} --showmotifs -o {} > {}_kpca.log 2> {}_kpca.err'\
    .format( path_to_scripts, organism, clones_file, kpca_clone_data_file, clones_file, clones_file )
run(cmd)
