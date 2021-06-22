import numpy as np
import sys
from genetic_code import reverse_genetic_code
from amino_acids import amino_acids
import csvfile

aa2nuc = {}
for aa in amino_acids:
    aa2nuc[aa] = reverse_genetic_code[aa][0]

def make_fake_cdr3_nucseq( cdr3 ):
    return ''.join( aa2nuc[x] for x in cdr3 )


headers = 'cell_id subject clone_size va_gene va_genes ja_gene ja_genes vb_gene vb_genes jb_gene jb_genes cdr3a cdr3a_nucseq cdr3b cdr3b_nucseq'.split()
#Cell_Index,Total_VDJ_Read_Count,Total_VDJ_Molecule_Count,TCR_Alpha_Gamma_V_gene_Dominant,TCR_Alpha_Gamma_J_gene_Dominant,TCR_Alpha_Gamma_C_gene_Dominant,TCR_Alpha_Gamma_CDR3_Nucleotide_Dominant,TCR_Alpha_Gamma_CDR3_Translation_Dominant,TCR_Alpha_Gamma_Read_Count,TCR_Alpha_Gamma_Molecule_Count,TCR_Beta_Delta_V_gene_Dominant,TCR_Beta_Delta_D_gene_Dominant,TCR_Beta_Delta_J_gene_Dominant,TCR_Beta_Delta_C_gene_Dominant,TCR_Beta_Delta_CDR3_Nucleotide_Dominant,TCR_Beta_Delta_CDR3_Translation_Dominant,TCR_Beta_Delta_Read_Count,TCR_Beta_Delta_Molecule_Count,TCR_Paired_Chains,Cell_Type_Experimental

def make_cell_file(inpath, outpath):
    infile = csvfile.InFile(inpath)
    outfile = csvfile.OutFile(outpath, headers)
    inhead = infile.headers
    line = infile.readline()
    while line != None:
        out = {}
        is_cell = True
        
        out['cell_id'] = line['Cell_Index']
        out['subject'] = 'UNK_S'
        out['clone_size'] = 0
        
        for ab in ('a', 'b'):
            bd_names = {'a':'Alpha_Gamma', 'b':'Beta_Delta'}
            for gene in ('v','j'):
                genes = line['TCR_'+bd_names[ab]+'_'+gene.upper() + '_gene_Dominant']
                is_cell &= genes != ''
                out[gene+ab+'_gene'] = genes.split(';')[0]
                out[gene+ab+'_genes'] = genes
            #cdr3
            cdr3 = line['TCR_'+bd_names[ab]+'_CDR3_Translation_Dominant']
            nucseq = line['TCR_'+bd_names[ab]+'_CDR3_Nucleotide_Dominant']
            is_cell &= cdr3 != '' and cdr3.count('[') == 0 and all([i in amino_acids for i in cdr3]) and all([i in 'ACTG' for i in nucseq])
            out['cdr3'+ab] = cdr3
            out['cdr3'+ab+'_nucseq'] = nucseq
        if is_cell:
            outfile.writeline(out)
        line = infile.readline()
    outfile.close()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        make_cell_file(sys.argv[1], sys.argv[2])
        
        csvfile.view(sys.argv[2])
    else:
        print "usage: make_cell_file_bd.py input_file.csv output_cell_file.csv"
