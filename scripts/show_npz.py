#!/usr/bin/env python2

import numpy
import sys
import code

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib


numpy.set_printoptions(threshold='nan')
numpy.set_printoptions(linewidth=100000000)

def get_corr_from_cov(cov_matrix):
	corr_matrix = numpy.zeros(cov_matrix.shape)
	for j in range(0,cov_matrix.shape[0]):
		for k in range(0, cov_matrix.shape[1]):
			corr_matrix[j][k] =  cov_matrix[j][k] / (numpy.sqrt(cov_matrix[j][j]) * numpy.sqrt(cov_matrix[k][k]))
	return corr_matrix

args = sys.argv[1:]
data = {}
for filename in args:
    npz = numpy.load(filename)
    for arr in npz.files:
	data[arr] = npz[arr]
#for item in data.files:
#	print item
#	print data[item]
print sorted(data.keys())
print "All data in dic 'data'"
code.interact(local=locals())


