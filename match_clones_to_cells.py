import numpy as np
from sys import argv
from csv_file_helper import *
from basic import *


with Parser(locals()) as p:
    p.str('clones_file').shorthand('c').required()
    p.str('output_file').shorthand('o').required()


clone2barcodes = eval(file('clonotype2barcodes.json','r').read())

clone_data, clone_ids, rows = read_csv_file(clones_file, True, True, True)

num_cells = sum(map(len, clone2barcodes.values()))

new_data = np.zeros((num_cells,clone_data.shape[1]), dtype=clone_data.dtype)
barcodes = []
new_data_index = 0

for i in range(clone_data.shape[0]):
    line = clone_data[i,:]
    barcodes.extend(clone2barcodes[clone_ids[i]])
    for barcode in clone2barcodes[clone_ids[i]]:
        new_data[new_data_index,:] = line
        new_data_index += 1

new_data = new_data[:new_data_index,:]

print new_data.shape, len(barcodes), len(rows)

write_csv_file(output_file, new_data, rownames = barcodes, colnames = ['barcode'] + rows[1:])
