import numpy as np
import sys
from genetic_code import reverse_genetic_code
from amino_acids import amino_acids

aa2nuc = {}
for aa in amino_acids:
    aa2nuc[aa] = reverse_genetic_code[aa][0]

def make_fake_cdr3_nucseq( cdr3 ):
    return ''.join( aa2nuc[x] for x in cdr3 )


headers = 'clone_id clonotype subject clone_size va_gene va_genes ja_gene ja_genes vb_gene vb_genes jb_gene jb_genes cdr3a cdr3a_nucseq cdr3b cdr3b_nucseq'.split()

def make_cell_file(inpath, outpath, outsep = ','):
    infile = open(inpath)
    outfile = open(outpath,'w')
    inhead = infile.readline().split(',')
    outfile.write(outsep.join(headers)+'\n')
    for strline in infile:
        line = dict(zip(inhead, strline.split(',')))
        out = dict(zip(headers, ['' for i in range(len(headers))]))
        is_cell = True
        
        out['clone_id'] = line['Cell_Index'] 
        out['subject'] = 'UNK_S'
        out['clone_size'] = 1
        
        for ab in ('a', 'b'):
            for gene in ('v','j'):
                genes = line['TCR'+ab+' '+gene.upper()]
                is_cell &= genes != ''
                out[gene+ab+'_gene'] = genes.split(';')[0]
                out[gene+ab+'_genes'] = genes
            #cdr3
            cdr3 = line['TCR'+ab+' AA CDR3']
            is_cell &= cdr3 != '' and cdr3.count('[') == 0
            out['cdr3'+ab] = cdr3
            out['cdr3'+ab+'_nucseq'] = make_fake_cdr3_nucseq(cdr3) if is_cell else ''
        if is_cell:
            outline = ''
            for head in headers:
                outline += str(out[head]) + outsep
            outfile.write(outline[:-1] + '\n')
    outfile.close()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        sep = ','
        if (sys.argv[2].split('.')[-1] == 'tsv'):
            sep = '\t'
        make_cell_file(sys.argv[1], sys.argv[2], sep)
    else:
        print "usage: make_cell_file_bd.py input_file.csv output_clones_file.csv"

