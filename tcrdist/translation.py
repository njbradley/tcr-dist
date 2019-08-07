import numpy as np

from . import logo_tools
from .genetic_code import genetic_code

def modifyGeneticCode(genetic_code):
    bases_plus = logo_tools.nucleotide_classes_lower_case.keys()

    for a in bases_plus:
        for b in bases_plus:
            for c in bases_plus:
                codon = a+b+c
                if codon in genetic_code: continue

                aas = []
                for a1 in logo_tools.nucleotide_classes_lower_case[a]:
                    for b1 in logo_tools.nucleotide_classes_lower_case[b]:
                        for c1 in logo_tools.nucleotide_classes_lower_case[c]:
                            aas.append( genetic_code[ a1+b1+c1 ] )
                if min(aas) == max(aas):
                    genetic_code[codon] = aas[0]
                else:
                    genetic_code[codon] = 'X'
    return genetic_code

def get_translation(seq, frame):
    assert frame in [-1, -2, -3, 1, 2, 3, '+1', '+2', '+3', '1', '2', '3', '-1', '-2', '-3']
    frame = int(frame)
    if frame < 0:
        seq = logo_tools.reverse_complement( seq )
    offset = np.abs(frame) - 1
    assert offset in range(3)
    seq = seq[offset:].lower()
    naa = len(seq)/3
    protseq = ''
    codons = []
    for i in range(naa):
        codon = seq[3*i:3*i+3]
        codons.append( codon )
        if '#' in codon:
            protseq += '#'
        else:
            protseq += genetic_code.get( codon, 'X' )
    return protseq,codons

genetic_code = modifyGeneticCode(genetic_code)

if __name__ == '__main__':
    print(modifyGeneticCode(genetic_code))