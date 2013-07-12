import matplotlib



def prepare_matplotlib():

	matplotlib.use('agg')
	import matplotlib.pyplot as plt

	matplotlib.rcParams['lines.linewidth'] = 2
	matplotlib.rcParams['font.family'] = 'sans-serif'
	matplotlib.rcParams['font.style'] = 'normal'
	matplotlib.rcParams['font.size'] = 22.
	matplotlib.rcParams['text.usetex'] = False
	#Axes
	matplotlib.rcParams['axes.linewidth'] = 2.0
	#Saving
	matplotlib.rcParams['savefig.bbox'] = 'tight'
	matplotlib.rcParams['savefig.dpi'] = 300



def apply_fig_cms_style(fig, **kwargs):

	fig.text(0.0,1.0, "CMS Preliminary",
			va = 'top', ha='right',
			transform=fig.transFigure, color='black')


def apply_ax_cms_style(ax, **kwargs):
	ax.text(0.0,1.0, kwargs.get('cms_text',"CMS Preliminary"),
			va = 'bottom', ha='left',
			transform=ax.transAxes, color='black')

	ax.text(1.0,1.0, kwargs.get('cme',r"$sqrt(s) = 7\/ \mathrm{TeV}$"),
			va = 'bottom', ha='right',
			transform=ax.transAxes, color='black')


def apply_ratio_plot_defaults(ax, **kwargs):
	defaults = {'set_xscale' : 'log',
				'set_yscale' : 'linear'}
	defaults.update(kwargs)
	
	for key, value in defaults.iteritems():
		attr = getattr(ax, key)
		if callable(attr):
			attr(value)
		else:
			setattr(ax, key,value)


def apply_spectrum_plot_defaults(ax, **kwargs):

	defaults = {'set_xscale' : 'log',
				'set_yscale' : 'log'}
	defaults.update(kwargs)
	
	for key, value in defaults.iteritems():
		attr = getattr(ax, key)
		if callable(attr):
			attr(value)
		else:
			setattr(ax, key, value)


