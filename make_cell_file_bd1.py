import numpy as np
import sys
from genetic_code import reverse_genetic_code
from amino_acids import amino_acids

aa2nuc = {}
for aa in amino_acids:
    aa2nuc[aa] = reverse_genetic_code[aa][0]

def make_fake_cdr3_nucseq( cdr3 ):
    return ''.join( aa2nuc[x] for x in cdr3 )


headers = 'clone_id clonotype subject clone_size va_gene va_genes ja_gene ja_genes vb_gene vb_genes jb_gene jb_genes cdr3a cdr3a_nucseq cdr3b cdr3b_nucseq num_alphas num_betas'.split()
outhead = dict(list(zip(headers, range(len(headers)))))



def make_cell_file(inpath, outpath):
    inp = np.loadtxt(inpath,'|S100', delimiter = ',')
    out = np.zeros((inp.shape[0]-1, len(headers)), dtype='|S100')
    is_cell = np.zeros((inp.shape[0]-1,), dtype = bool)
    inhead = dict(list(zip(inp[0,:].tolist(), range(inp.shape[1]))))
    inp = inp[1:,:]
    is_cell[...] = True
    
    #clone_id, subject, clone size
    out[:,outhead['clone_id']] = inp[:,inhead['Cell_Index']]
    out[:,outhead['subject']] = 'UNK_S'
    out[:,outhead['clone_size']] = 1
    # v, j genes
    for ab in ('a', 'b'):
        for gene in ('v','j'):
            genes = inp[:,inhead['TCR'+ab+' '+gene.upper()]]
            is_cell = is_cell & (genes != '')
            genes_split = np.char.split(genes,';')
            out[:,outhead[gene+ab+'_gene']] = np.array([i[0] for i in genes_split])
            out[:,outhead[gene+ab+'_genes']] = genes
        #cdr3
        cdr3 = inp[:,inhead['TCR'+ab+' AA CDR3']]
        cdr3_nuc = np.array([make_fake_cdr3_nucseq(i) for i in cdr3])
        out[:,outhead['cdr3'+ab]] = cdr3
        is_cell = is_cell & (cdr3 != '') & (np.char.count(cdr3,'[') == 0)
    out = out[is_cell,:]
    out = np.concatenate( (np.array([headers]), out), axis=0)
    np.savetxt(outpath, out, '%s', delimiter = ',')


if __name__ == "__main__":
    if len(sys.argv) == 3:
        make_cell_file(sys.argv[1], sys.argv[2])
    else:
        print "usage: make_cell_file_bd.py input_file.csv output_file.csv"

