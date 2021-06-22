from amino_acids import HP, GES, KD, aa_charge, amino_acids
import parse_tsv
from basic import *
import numpy as np
import csvfile
#from csv_file_helper import *

with Parser(locals()) as p:
    p.str('clones_file').required()
    p.str('output_file').shorthand('o').required()

def get_charge( cdr3 ):
    return sum( ( aa_charge.get(x,0.0) for x in cdr3 ) )

def get_hp1( cdr3 ):
    return sum( ( -1*GES.get(x,0.0) for x in cdr3 ) )

def get_hp2( cdr3 ):
    return sum( ( HP.get(x,0.0) for x in cdr3 ) )
    #return sum( ( KD.get(x,0.0) for x in cdr3 ) )




#all_tcrs = parse_tsv.parse_tsv_file( clones_file, ['clone_id'], ['cdr3a','cdr3b','clone_size'] )
ifile = csvfile.InFile(clones_file)

functions = {'charge':get_charge, 'hydro1':get_hp1, 'hydro2':get_hp2, 'length':len}

#data = np.zeros((len(all_tcrs), len(functions)*3))

#rows = []

cols = ['clone_id']

for name in ('a','b','ab'):
    for func_name in functions:
        cols.append(func_name + '_' + name)

ofile = csvfile.OutFile(output_file, cols)

#for i,clonotype in enumerate(all_tcrs):
    #rows.append(clonotype)
line = ifile.readline()
while None != line:
    #a,b,clone_size = all_tcrs[clonotype][0]
    #'cdr3a','cdr3b','clone_size'
    a = line['cdr3a']
    b = line['cdr3b']
    clone_size = line['clone_size']
    ab = a+b
    newline = {'clone_id': line['clone_id']}
    for name, tcrs in (('a',a), ('b',b), ('ab',ab)):
        for func_name in functions:
            newline[func_name + '_' + name] = functions[func_name](tcrs)
    ofile.writeline(newline)
    line = ifile.readline()

ofile.close()

csvfile.view(output_file)
##write_csv_file(output_file, data, rows, cols)
