import numpy as np
from sys import argv
from csv_file_helper import *
from basic import *

with Parser(locals()) as p:
    p.str('cell_file').shorthand('f').required()
    p.str('clone_file').shorthand('c').required()
    p.str('output_file').shorthand('o').required()


cell_data, _, cell_col = read_csv_file(cell_file, False, True, True)

clone_data, clone_ids, rows = read_csv_file(clone_file, True, True)


array = np.empty([cell_data.shape[0], clone_data.shape[1]], dtype='|S30')
print array.shape


new_rows = cell_data[:,0].tolist()[:][1:] + ['']
new_cols = ['contig_id'] + rows[1:]


i = 0
for cell_index in range(len(new_rows)):
    clonetype = cell_data[cell_index,16]
    if i%50 == 0:
        print clonetype,i
    if clonetype in clone_ids:
        index = clone_ids.index(clonetype)
        data = clone_data[index,:]
        array[i,:] = data
        i += 1
    else:
        new_rows.pop(i)

array = array[:i,:]

print len(new_rows), len(new_cols), array.shape


write_csv_file(output_file, array, new_rows, new_cols)
