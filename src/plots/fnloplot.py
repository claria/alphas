#! /usr/bin/env python2

import os

import plotting
plotting.prepare_matplotlib()
import matplotlib.pyplot as plt

import fnlo

def main():

	produce_ratio_plot()


def produce_ratio_plot(*args, **kwargs):

	fig = plt.figure(figsize=(12,8))

	ax = fig.add_subplot(111)
	plotting.apply_ax_cms_style(ax)
	plotting.apply_ratio_plot_defaults(ax)

	theory = fnlo.fnlo('/home/aem/uni/ana/alphas/tables/fnl2332d.tab', 
						'CT10.LHgrid')
	
	pt_down, pt_up = theory.get_bins_down()[0], theory.get_bins_up()[0]
	y_down, y_up = theory.get_bins_down()[1], theory.get_bins_up()[1]
	xsnlo = theory.get_central_crosssection()
	pdf_uncert = theory.get_pdf_uncert()
	ax.fill_between(pt_down[y_down == 0.0], 
			1 - pdf_uncert[0][y_down == 0.]/xsnlo[y_down == 0.],
			1 + pdf_uncert[1][y_down == 0.]/xsnlo[y_down == 0.])
	#ax.plot(pt_down[y_down == 0.0], xsnlo[y_down == 0.0])
	
	output_dir = 'test'

	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	fig.savefig('test.pdf', bbox_inches='tight', dpi=300)


if __name__ == '__main__':
	main()
