from __future__ import absolute_import, division, print_function
import os.path as op
import numpy as np
import pandas as pd
import numpy.testing as npt
import pytest

import tcrdist as td

datasetsPath = op.join(td.__path__[0], 'datasets')

tempSkip = pytest.mark.skip(reason="Temporarily skipping for efficiency.")

alphaNT = 'TACAGCAGGGTTTTGTCTGTGATATACCATCAGAATCCTTACTTTGTGACACATTTGTTTGAGAATCAAAATCGGTGAATAGGCAGACAGACTTGTCACTGGATTTAGAGTCTCTCAGCTGGTACACGGCAGGGTCAGGGTTCTGGATATTTGGTTTAACAGAGAGTTTAGTGCCTTTTCCAAAGATGAGATTTCCTTGGCTTGCTTGCCCAGCACAGAAGTAGATGCCTACATCACTAGGTATGGATGCTGAGATATTCAGGAAGCTGTCCTTTCTGGTTATACCAAACTGAGCAGTCAGTCTTCCATTTGAGGTCAATTCACCAGCCTTATATAAGGCTATCAAGAGGACAGGACCTTCCCCAGGGTCCTGCTTGTACCATAGCCAGGTATTAAATATGCTTGAAGAAGTGCAGTTCATGGAGACATCTTCTCCTTCCTGGATAAACATAGATTGAGGACTCTGATTCAGCCTGTTGACCACCNAGGNGTGGAGTGATCTCAAGCTGTACACCCTACCTTGGCTCTGGCTCTCTTCTTCTTGGCCGCCGCCCGGGCTTTCGCTCTGGCNCAGCCTAACTTTTTTAACCAAATGCGAAACCGCCTGCCGGTCCCCCAAG'
betaNT = 'CGGGGGGGGTACCNTTGNTTAGGTCCTCTACACGGTTAACCTGGTCCCCGAACCGAAGGTCAATAGGGCCTGTATACTGCTGGCACAGAAGTACACAGCTGAGTCCCTGGGTTCTGAGGGCTGGATCTTCAGAGTGGAGTCANN'
alphaQuals = '6.6.6.6.11.9.9.6.6.6.6.7.7.22.32.37.37.37.37.25.24.18.18.15.17.9.9.9.22.19.34.34.37.37.47.47.47.47.53.53.53.50.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.57.59.68.68.68.57.57.57.57.57.59.59.68.68.68.68.68.68.57.59.59.59.57.57.57.68.68.68.68.68.68.68.68.68.68.68.57.57.57.57.57.57.57.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.62.62.62.62.62.62.68.68.68.68.68.68.68.68.68.68.62.62.62.62.62.62.62.68.68.68.68.68.68.68.62.62.62.62.62.62.62.68.68.68.68.68.62.62.62.62.62.62.62.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.62.62.62.62.68.62.62.68.68.68.68.68.68.68.62.62.62.62.62.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.59.59.59.59.59.59.59.68.68.68.59.59.59.57.57.59.59.59.68.68.68.68.59.59.59.57.68.68.68.68.68.59.59.59.68.68.68.68.59.59.59.59.59.59.59.59.68.68.68.59.59.57.59.57.57.57.38.33.12.12.12.27.36.43.43.24.29.28.17.14.38.38.47.47.57.57.57.57.57.57.57.57.57.59.48.48.48.48.57.57.57.47.57.43.57.47.57.57.57.57.46.46.43.43.43.44.57.48.59.59.59.57.57.57.59.54.54.54.48.43.43.43.43.47.47.54.47.47.43.32.37.31.39.35.47.40.47.48.47.47.47.36.36.36.43.37.24.18.18.12.19.19.33.43.46.39.41.23.23.11.8.3.0.3.8.3.0.3.8.9.10.10.11.10.10.9.9.9.9.10.13.18.17.13.8.8.8.10.8.8.7.8.8.8.8.8.6.6.6.6.7.7.9.10.10.10.10.13.13.13.13.8.8.8.8.8.8.8.8.9.15.15.9.8.8.8.9.10.18.19.25.14.10.8.10.8.8.8.8.8.8.8.8.8.8.8.3.0.3.9.10.12.12.10.8.8.8.10.8.8.11.11.10.9.10.10.10.8.11.14.9.10.8.12.9.11.9.12.10.10.10.10.8.9.8.8.8.7.8.8.9.10.10.8.8.7.7'
betaQuals = '12.12.12.12.12.22.9.8.6.6.6.8.3.0.3.10.3.0.3.10.10.11.20.25.30.37.37.29.27.14.14.15.27.30.41.47.36.50.50.50.42.42.57.57.43.47.53.47.47.47.47.47.47.50.54.57.57.57.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.57.57.57.57.59.59.59.57.57.57.57.57.57.57.57.59.57.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.68.59.59.59.59.59.57.57.57.59.57.57.43.37.28.28.21.28.23.37.28.30.15.19.17.15.21.20.25.3.0.0'

#@tempSkip
def test_process_nt():
    chain = td.processing.processNT('human', 'A', alphaNT, alphaQuals)
    assert type(chain) is td.TCRChain

    chain = td.processing.processNT('human', 'B', betaNT, betaQuals)
    assert type(chain) is td.TCRChain

#@tempSkip
def test_human_paired_dataset():
    df = td.processing.readPairedSequences('human', op.join(datasetsPath, 'test_human_pairseqs.tsv'))
    assert df.shape[0] == 20
    
    """Could be checkig that all the columns we expect are present in df"""
    
    """Only status allowed is ['OK']"""
    assert df['a_status'].unique().shape[0] == 1
    assert df['b_status'].unique().shape[0] == 1

#@tempSkip
def test_mouse_paired_dataset():
    df = td.processing.readPairedSequences('mouse', op.join(datasetsPath, 'test_mouse_pairseqs.tsv'))
    assert df.shape[0] == 20
    assert df['a_status'].unique().shape[0] == 1
    assert df['b_status'].unique().shape[0] == 1

#@tempSkip
def test_compute_probs():
    psDf = td.processing.readPairedSequences('mouse', op.join(datasetsPath, 'test_mouse_pairseqs.tsv'))
    
    probDf = td.processing.computeProbs(psDf,
                                         add_masked_seqs=True,
                                         filterOut=False,
                                         max_cdr3_length=30,
                                         allow_stop_codons=False,
                                         allow_X=False)
    assert probDf.shape[0] == psDf.shape[0]

#@tempSkip
def test_datasets():
    psDf = td.datasets.loadPSData('test_human_pairseqs')
    assert psDf.shape[0] == 20

#@tempSkip
def test_find_clones():
    psDf = td.processing.readPairedSequences('human', op.join(datasetsPath, 'test_human_pairseqs.tsv'))
    probDf = td.processing.computeProbs(psDf)
    psDf = psDf.join(probDf)
    clonesDf = td.processing.identifyClones(psDf)
    