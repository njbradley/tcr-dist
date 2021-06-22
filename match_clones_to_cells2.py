import numpy as np
import csvfile
from sys import argv
from csv_file_helper import *
from basic import *


with Parser(locals()) as p:
    p.str('clones_file').shorthand('c').required()
    p.str('output_file').shorthand('o').required()
    p.str('clone_id').default('');

clone2barcodes = eval(file('clonotype2barcodes.json','r').read())

ifile = csvfile.InFile(clones_file);
if clone_id == '':
    clone_id = ifile.headers[0]
    print "clone_id not specified, using '" + clone_id + "'"

out_headers = ifile.headers[:]
out_headers.insert(1,'clone_size')
out_headers[out_headers.index(clone_id)] = 'barcode'
ofile = csvfile.OutFile(output_file, out_headers)

line = ifile.readline();
while line != None:
    id = line[clone_id]
    barcodes = clone2barcodes[id]
    clone_size = len(barcodes)
    del line[clone_id]
    for barc in barcodes:
        line['barcode'] = barc
        line['clone_size'] = clone_size
        ofile.writeline(line)
    line = ifile.readline()

ofile.close()

csvfile.view(output_file)
