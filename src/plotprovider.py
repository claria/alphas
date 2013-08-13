import os

import matplotlib
import numpy
from numpy.polynomial import Polynomial

from config import config
from src.libs.arraydict import ArrayDict

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


class SimplePlot(object):

    def __init__(self):
        self.prepare_matplotlib()
        self.fig = plt.figure()

    def prepare(self, **kwargs):
        """
        Before plotting:
        Add axes to Figure, etc
        """
        self.ax = self.fig.add_subplot(1, 1, 1)

    def produce(self):
        """
        Do the Plotting
        """
        pass

    def finalize(self, filepath='test.pdf'):
        """
        Apply final settings, autoscale etc
        Save the plot
        :param filepath:
        """

        self.autoscale(margin=0.1)

        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.fig.savefig(filepath)

    def prepare_matplotlib(self):
        # matplotlib.use('agg')
        # matplotlib.use('pdf')

        matplotlib.rcParams['lines.linewidth'] = 2
        matplotlib.rcParams['font.family'] = 'sans-serif'
        matplotlib.rcParams['font.style'] = 'normal'
        matplotlib.rcParams['font.size'] = 22.
        matplotlib.rcParams['legend.fontsize'] = 14.
        matplotlib.rcParams['text.usetex'] = False
        # Axes
        matplotlib.rcParams['axes.linewidth'] = 2.0
        # Saving
        matplotlib.rcParams['savefig.bbox'] = 'tight'
        matplotlib.rcParams['savefig.dpi'] = 300
        matplotlib.rcParams['savefig.format'] = 'pdf'

    #
    # Helper functions
    #

    def set_style(self, style, **kwargs):
        """
        Some preset styles
        """
        if style == 'cmsprel':
            self.ax.text(0.0, 1.01, "CMS Preliminary",
                         va='bottom', ha='left',
                         transform=self.ax.transAxes, color='black')
            self.ax.text(1.0, 1.01,
                         kwargs.get('cme', r"$\sqrt{s} = 7\/ \mathrm{TeV}$"),
                         va='bottom', ha='right',
                         transform=self.ax.transAxes, color='black')
        elif style == 'cms':
            self.ax.text(0.0, 1.01, "CMS",
                         va='bottom', ha='left',
                         transform=self.ax.transAxes, color='black')
            self.ax.text(1.0, 1.01,
                         kwargs.get('cme', r"$\sqrt{s} = 7\/ \mathrm{TeV}$"),
                         va='bottom', ha='right',
                         transform=self.ax.transAxes, color='black')

    def autoscale(self, xmargin=0.0, ymargin=0.0, margin=0.0):
        # User defined autoscale with margins
        x0, x1 = tuple(self.ax.dataLim.intervalx)
        if margin > 0:
            xmargin = margin
            ymargin = margin
        if xmargin > 0:
            if self.ax.get_xscale() == 'linear':
                delta = (x1 - x0) * xmargin
                x0 -= delta
                x1 += delta
            else:
                delta = (x1 / x0) ** xmargin
                x0 /= delta
                x1 *= delta
            self.ax.set_xlim(x0, x1)
        y0, y1 = tuple(self.ax.dataLim.intervaly)
        if ymargin > 0:
            if self.ax.get_yscale() == 'linear':
                delta = (y1 - y0) * ymargin
                y0 -= delta
                y1 += delta
            else:
                delta = (y1 / y0) ** ymargin
                y0 /= delta
                y1 *= delta
            self.ax.set_ylim(y0, y1)

    def log_locator_filter(self, x, pos):
        """Add minor tick labels in log plots at 2* and 5*
        """
        s = str(int(x))
        if len(s) == 4:
            return ''
        if s[0] in ('2', '5'):
            return s
        return ''

    def steppify_bin(self, arr, isx=False):
        """Produce stepped array of arr, also of x
        """
        if isx:
            newarr = numpy.array(zip(arr[0], arr[1])).ravel()
        else:
            newarr = numpy.array(zip(arr, arr)).ravel()
        return newarr


class AlphasSensitivityPlot(SimplePlot):

    def __init__(self, measurements=None):
        super(AlphasSensitivityPlot, self).__init__()
        self.measurements = measurements
        self.prepare()
        self.set_style(style='cmsprel')

    def prepare(self):
        super(AlphasSensitivityPlot, self).prepare()

        self.ax.set_xscale('log')
        minorLocator = MultipleLocator(0.1)
        self.ax.yaxis.set_minor_locator(minorLocator)
        self.ax.xaxis.set_minor_formatter(
            plt.FuncFormatter(self.log_locator_filter))

        bin_down = self.measurements[0].get_source('ylow')()[0]
        bin_up = self.measurements[0].get_source('yhigh')()[0]
        if bin_down != 0.:
            ybin_label = "${0} \leq |y| < {1}$".format(bin_down, bin_up)
        else:
            ybin_label = "$|y| < {0}$".format(bin_up)

        self.ax.text(0.02, 0.85, ybin_label, va='bottom',
                     ha='left', transform=self.ax.transAxes, color='black')

    def produce_plot(self):

        ref_measurement = self.measurements[0]
        min_measurement = self.measurements[0]
        max_measurement = self.measurements[0]
        for measurement in self.measurements:
            # Find central PDF
            if measurement.pdf_config.get('central', 'False') == 'True':
                ref_measurement = measurement
            if (max_measurement.pdf_config.as_float('alphas') <
                    measurement.pdf_config.as_float('alphas')):
                max_measurement = measurement
            if (min_measurement.pdf_config.as_float('alphas') >
                    measurement.pdf_config.as_float('alphas')):
                min_measurement = measurement

        exp_unc = ref_measurement.get_diagonal_unc(origin=('exp',))
        stat_unc = ref_measurement.get_diagonal_unc(label=('stat',))
        self.ax.errorbar(x=ref_measurement.get_bin_mid('pt'),
                         xerr=ref_measurement.get_bin_error('pt'),
                         y=ref_measurement.data / ref_measurement.theory,
                         yerr=stat_unc / ref_measurement.theory,
                         fmt='o',
                         capthick=2,
                         color='black')

        self.ax.fill_between(
            x=self.steppify_bin(ref_measurement.get_bin('pt').T, isx=True),
            y1=self.steppify_bin((ref_measurement.data - exp_unc[
                0]) / ref_measurement.theory, isx=False),
            y2=self.steppify_bin((ref_measurement.data + exp_unc[
                1]) / ref_measurement.theory, isx=False),
            hatch='//', alpha=1.0, color='none',
            edgecolor='Gold')

        self.ax.plot(
            self.steppify_bin(ref_measurement.get_bin('pt').T, isx=True),
            self.steppify_bin(
                ref_measurement.theory / ref_measurement.theory,
                isx=False),
            color='red', linestyle='-', linewidth=2)

        self.ax.text(0.02, 0.98, ref_measurement.pdf_set, va='top',
                     ha='left', transform=self.ax.transAxes, color='black')

        for idx, measurement in enumerate(self.measurements):
            if measurement is ref_measurement:
                continue
            color = 'grey'
            linestyle = '--'
            linewidth = 1
            if measurement is min_measurement:
                color = 'green'
                linewidth = 2
            if measurement is max_measurement:
                color = 'blue'
                linewidth = 2

                # new_color = next(ax._get_lines.color_cycle)
            self.ax.plot(
                self.steppify_bin(measurement.get_bin('pt').T, isx=True),
                self.steppify_bin(
                    measurement.theory / ref_measurement.theory,
                    isx=False),
                color=color, linestyle=linestyle, linewidth=linewidth)


class DataTheoryRatio(SimplePlot):

    def __init__(self, measurements=None):
        super(DataTheoryRatio, self).__init__()
        self.measurements = measurements
        self.prepare()
        self.set_style(style='cmsprel')

    def prepare(self):
        super(DataTheoryRatio, self).prepare()
        self.ax.set_xscale('log')
        minorLocator = MultipleLocator(0.1)
        self.ax.yaxis.set_minor_locator(minorLocator)
        self.ax.xaxis.set_minor_formatter(
            plt.FuncFormatter(self.log_locator_filter))

        self.ax.tick_params(which='major', length=8, width=1.5)
        self.ax.tick_params(which='minor', length=4, width=1)
        self.ax.yaxis.grid(True)

        bin_down = self.measurements[0].get_source('ylow')()[0]
        bin_up = self.measurements[0].get_source('yhigh')()[0]
        if bin_down != 0.:
            ybin_label = "${0} \leq |y| < {1}$".format(bin_down, bin_up)
        else:
            ybin_label = "$|y| < {0}$".format(bin_up)

        self.ax.text(0.02, 0.85, ybin_label, va='bottom',
                     ha='left', transform=self.ax.transAxes, color='black')

    def produce_plot(self):

        ref_measurement = self.measurements[0]
        exp_unc = ref_measurement.get_diagonal_unc(origin=('exp',))
        stat_unc = ref_measurement.get_diagonal_unc(label=('stat',))
        theo_unc = ref_measurement.get_diagonal_unc(origin=('theo',))

        # print ','.join(map(str, ref_measurement.get_source('ptlow')()))
        # print ','.join(map(str, ref_measurement.get_source('xsnlo')()))

        self.ax.errorbar(x=ref_measurement.get_bin_mid('pt'),
                         xerr=ref_measurement.get_bin_error('pt'),
                         y=ref_measurement.data / ref_measurement.theory,
                         yerr=stat_unc / ref_measurement.theory,
                         fmt='o',
                         capthick=2,
                         color='black')

        self.ax.fill_between(
            x=self.steppify_bin(ref_measurement.get_bin('pt').T, isx=True),
            y1=self.steppify_bin((ref_measurement.data - exp_unc[
                0]) / ref_measurement.theory, isx=False),
            y2=self.steppify_bin((ref_measurement.data + exp_unc[
                1]) / ref_measurement.theory, isx=False),
            hatch='//', alpha=1.0, color='none',
            edgecolor='Gold')

        self.ax.text(0.02, 0.98, ref_measurement.pdf_set, va='top',
                     ha='left', transform=self.ax.transAxes, color='black')

        for measurement in self.measurements:
            color = next(self.ax._get_lines.color_cycle)
            self.ax.fill_between(
                x=self.steppify_bin(measurement.get_bin('pt').T, isx=True),
                y1=self.steppify_bin((measurement.theory - theo_unc[
                    0]) / ref_measurement.theory, isx=False),
                y2=self.steppify_bin((measurement.theory + theo_unc[
                    1]) / ref_measurement.theory, isx=False),
                hatch='//', alpha=1.0, color='none',
                edgecolor=color)

            self.ax.plot(self.steppify_bin(ref_measurement.get_bin('pt').T,
                                           isx=True),
                         self.steppify_bin(measurement.theory /
                                           ref_measurement.theory),
                         color=color, linestyle='-', linewidth=2)

            p = matplotlib.patches.Rectangle((1, 1), 0, 0,
                                             label=measurement.pdf_set,
                                             hatch='//', alpha=1.0, fill=False,
                                             edgecolor=color)
            self.ax.add_patch(p)

        self.ax.set_xlabel(r'$p_\mathrm{T}$ (GeV)')
        self.ax.set_ylabel('Ratio to {0}'.format(ref_measurement.pdf_set))

        self.ax.legend(loc='best')


class Chi2Distribution(SimplePlot):

    def __init__(self, analysis, pdf_family, scenario, scale):
        super(Chi2Distribution, self).__init__()
        self.prepare()
        self.set_style(style='cmsprel')
        cache_filepath = os.path.join(config.cache_chi2, analysis,
                                      '{}_{}_{}.npz'.format(pdf_family,
                                                            scenario,
                                                            scale))
        self.data = ArrayDict(cache_filepath)
        self.pdf_family = pdf_family
        self.analysis = analysis
        self.scale = scale

    def fit_polynomial(self, data, deg=2):

        poly = Polynomial.fit(data['alphas'], data['chi2'], deg)
        if numpy.isnan(numpy.min(poly.coef)):
            print 'RankWarning in fit'
            return None
        return poly

    def extract_voi(self, poly, data):

        poly_deriv = poly.deriv()
        voi = {}
        # Central as value
        voi['alphas'] = poly_deriv.roots()[0]
        # Chi2 of central value
        voi['chi2'] = poly(voi['alphas'])
        poly_shifted = poly - ([voi['chi2'] + 1., ] + [0, ])
        (down, up) = poly_shifted.roots()
        # Errors up and down
        voi['down'] = voi['alphas'] - down
        voi['up'] = up - voi['alphas']
        # NDOF and chi2ndof
        voi['ndof'] = data['ndof'][0]
        voi['chi2ndof'] = voi['chi2'] / voi['ndof']
        return voi

    def produce_plot(self):

        self.ax.scatter(x=self.data['alphas'], y=self.data['chi2'],
                        color='black', s=50)

        # Get Interpolation of Chi2 Values
        poly = self.fit_polynomial(self.data, deg=2)
        voi = self.extract_voi(poly, self.data)
        self.ax.plot(self.data['alphas'],
                     poly(self.data['alphas']), color='blue')

        alphas_text = r'$\alpha_s(M_\mathrm{{Z}}^2)={{{alphas:.4f}}}_{{-{down:.4f}}}^{{+{up:.4f}}}$'.format(
            **voi)
        self.ax.text(
            0.99, 0.99, "{}\n{}\n{}".format(
                self.pdf_family, alphas_text, self.scale),
            va='top', ha='right', ma='left',
            transform=self.ax.transAxes, color='black')
