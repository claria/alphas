import os

import matplotlib
import numpy
from numpy.polynomial import Polynomial

from alphas import get_measurement
from config import config
from src.libs.arraydict import ArrayDict


def fit_chi2_values(alphas, chi2, deg=2):
    poly = Polynomial.fit(alphas, chi2, deg)
    if numpy.isnan(numpy.min(poly.coef)):
        print 'RankWarning in fit'
        return None, None
    poly_deriv = poly.deriv()
    alphas = {'central': poly_deriv.roots()[0]}
    alphas['chi2'] = poly(alphas['central'])
    poly_shifted = poly - ([alphas['chi2'] + 1., ] + (deg - 1) * [0, ])
    (down, up) = poly_shifted.roots()
    alphas['down'] = alphas['central'] - down
    alphas['up'] = up - alphas['central']

    return poly, alphas


def prepare_matplotlib():
    #matplotlib.use('agg')
    #matplotlib.use('pdf')

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
    matplotlib.rcParams['savefig.format'] = 'png'


prepare_matplotlib()

import matplotlib.pyplot as plt


def printall(*args, **kwargs):
    print args
    print kwargs


def plot(*args, **kwargs):
    lhapdf_config = config.get_config('lhapdf2')
    ana_config = config.get_config(kwargs['analysis'])
    kwargs['pdf_sets'] += lhapdf_config['pdf_families'][kwargs['pdf_family']]

    for scale in ana_config['theory'].as_list('scales'):
        if kwargs['plot'] in ['ratio', 'asratio']:
            measurements = []
            for pdf_set in kwargs['pdf_sets']:
                kwargs['pdf_set'] = pdf_set
                kwargs['scale'] = scale
                measurements.append(get_measurement(**kwargs))

            #Split according to y bins of first (ref) measurement
            ylow = measurements[0].get_source('ylow')()
            ylow_set = set(ylow)
            for ylowbin in ylow_set:
                mask = (ylowbin == ylow)
                map(lambda x: x.set_mask(mask), measurements)
                if 'ratio' in kwargs['plots']:
                    fig = get_fig_data_theory_ratio(measurements)
                elif 'asratio' in kwargs['plots']:
                    fig = get_fig_as_sensitivity(measurements)
                fig.savefig('/home/aem/uni/ana/alphas2/test')
        elif kwargs['plot'] == 'chi2':

            fig = get_fig_chi2_distribution(scale, **kwargs)
            fig.savefig('/home/aem/uni/ana/alphas2/test')


def get_fig_chi2_distribution(scale, **kwargs):
    cache_filepath = os.path.join(config.cache_chi2,
                                  kwargs['analysis'],
                                  '{}_{}.npz'.format(
                                      kwargs['pdf_family'], scale))

    fig = get_default_figure()
    ax = fig.add_subplot(111)
    apply_ax_cms_style(ax)

    data = ArrayDict(cache_filepath)

    ax.scatter(x=data['alphas'], y=data['chi2'], color='black', s=50)

    #Get Interpolation of Chi2 Values
    poly, alphas = fit_chi2_values(data['alphas'], data['chi2'], deg=2)
    ax.plot(data['alphas'], poly(data['alphas']), color='blue')

    return fig


def get_fig_as_sensitivity(measurements, *args, **kwargs):
    fig = get_default_figure()
    ax = fig.add_subplot(111)
    apply_ax_cms_style(ax)
    apply_ratio_plot_defaults(ax)

    for idx, measurement in enumerate(measurements):
        x = measurement.get_bin_mid(label='pt')
        color = 'grey'
        linestyle = '--'
        if idx == 1:
            color = 'green'
        if idx == len(measurements) - 1:
            color = 'blue'
        if idx == 0:
            color = 'red'
            linestyle = '-'
            ref_meas = measurement
            exp_unc = measurement.get_diagonal_unc(origin=('exp',))
            stat_unc = measurement.get_diagonal_unc(label=('stat',))
            ax.errorbar(x=measurement.get_bin_mid('pt'),
                        xerr=measurement.get_bin_error('pt'),
                        y=measurement.data / ref_meas.theory,
                        yerr=stat_unc / ref_meas.theory,
                        fmt='o',
                        capthick=2,
                        color='black')

            ax.fill_between(x=steppify_bin(measurement.get_bin('pt'), isx=True),
                            y1=steppify_bin((measurement.data - exp_unc[
                                0]) / ref_meas.theory, isx=False),
                            y2=steppify_bin((measurement.data + exp_unc[
                                1]) / ref_meas.theory, isx=False),
                            hatch='/', alpha=1.0, color='none',
                            edgecolor='Gold')

        print measurement.pdf_set
        if measurement.pdf_set == ref_meas.pdf_set and idx != 0:
            continue
            # new_color = next(ax._get_lines.color_cycle)
        ax.plot(steppify_bin(measurement.get_bin('pt'), isx=True),
                steppify_bin(measurement.theory / ref_meas.theory, isx=False),
                color=color, linestyle=linestyle)

    ax.set_ylim((0.9 * ax.dataLim.ymin, 1.1 * ax.dataLim.ymax))
    ax.set_xlim((0.9 * ax.dataLim.xmin, 1.1 * ax.dataLim.xmax))
    return fig


def get_fig_data_theory_ratio(measurements, *args, **kwargs):
    fig = get_default_figure()
    ax = fig.add_subplot(111)
    apply_ax_cms_style(ax)
    apply_ratio_plot_defaults(ax)

    for idx, measurement in enumerate(measurements):
        x = measurement.get_bin_mid(label='pt')
        if idx == 0:
            ref_meas = measurement
            exp_unc = measurement.get_diagonal_unc(origin=('exp',))
            stat_unc = measurement.get_diagonal_unc(label=('stat',))
            ax.errorbar(x=measurement.get_bin_mid('pt'),
                        xerr=measurement.get_bin_error('pt'),
                        y=measurement.data / ref_meas.theory,
                        yerr=stat_unc / ref_meas.theory,
                        fmt='o',
                        capthick=2,
                        color='black')

            ax.fill_between(x=steppify_bin(measurement.get_bin('pt'), isx=True),
                            y1=steppify_bin((measurement.data - exp_unc[
                                0]) / ref_meas.theory, isx=False),
                            y2=steppify_bin((measurement.data + exp_unc[
                                1]) / ref_meas.theory, isx=False),
                            hatch='/', alpha=1.0, color='none',
                            edgecolor='Gold')

        theo_unc = measurement.get_diagonal_unc(origin=('theo',))
        new_color = next(ax._get_lines.color_cycle)
        ax.fill_between(x=steppify_bin(measurement.get_bin('pt'), isx=True),
                        y1=steppify_bin((measurement.theory - theo_unc[
                            0]) / ref_meas.theory, isx=False),
                        y2=steppify_bin((measurement.theory + theo_unc[
                            1]) / ref_meas.theory, isx=False),
                        hatch='/', alpha=1.0, color='none', edgecolor=new_color)
        ax.plot(steppify_bin(measurement.get_bin('pt'), isx=True),
                steppify_bin(measurement.theory / ref_meas.theory, isx=False),
                color=new_color)

    ax.set_ylim((0.9 * ax.dataLim.ymin, 1.1 * ax.dataLim.ymax))
    ax.set_xlim((0.9 * ax.dataLim.xmin, 1.1 * ax.dataLim.xmax))
    return fig


def get_default_figure():
    fig = plt.figure(figsize=(10, 8))
    return fig


#def apply_fig_cms_style(fig, **kwargs):
#    fig.text(0.0, 1.0, "CMS Preliminary",
#             va='top', ha='right',
#             transform=fig.transFigure, color='black')


def apply_ax_cms_style(ax, **kwargs):
    ax.text(0.0, 1.0, kwargs.get('cms_text', "CMS Preliminary"),
            va='bottom', ha='left',
            transform=ax.transAxes, color='black')

    ax.text(1.0, 1.0, kwargs.get('cme', r"$\sqrt{s} = 7\/ \mathrm{TeV}$"),
            va='bottom', ha='right',
            transform=ax.transAxes, color='black')


def apply_ratio_plot_defaults(ax, **kwargs):
    defaults = {'set_xscale': 'log',
                'set_yscale': 'linear'}
    defaults.update(kwargs)

    for key, value in defaults.iteritems():
        attr = getattr(ax, key)
        if callable(attr):
            attr(value)
        else:
            setattr(ax, key, value)


def apply_spectrum_plot_defaults(ax, **kwargs):
    defaults = {'set_xscale': 'log',
                'set_yscale': 'log'}
    defaults.update(kwargs)

    for key, value in defaults.iteritems():
        attr = getattr(ax, key)
        if callable(attr):
            attr(value)
        else:
            setattr(ax, key, value)


def steppify_bin(arr, isx=False, where='mid'):
    if isx:
        newarr = numpy.array(zip(arr[0], arr[1])).ravel()
    else:
        newarr = numpy.array(zip(arr, arr)).ravel()
    return newarr


def steppify(arr, isx=False, where='mid'):
    """
    *support function*
    Converts an array to double-length for step plotting
    """
    if isx:
        print "arr", arr
        print "arr1", arr[1:]
        print "arr2", arr[:-1]
        interval = numpy.abs(arr[1:] - arr[:-1]) / 2.0
        print "interval", interval
        newarr = numpy.array(
            zip(arr[:-1] - interval, arr[:-1] + interval)).ravel()
        print "newarr", newarr
        newarr = numpy.concatenate([newarr, 2 * [newarr[-1] + interval[-1]]])
    else:
        if where == 'mid':
            newarr = numpy.array(zip(arr, arr)).ravel()
        else:
            raise NotImplementedError("")

    return newarr
