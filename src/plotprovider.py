import os

import matplotlib
import numpy as np
from numpy.polynomial import Polynomial
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from src.libs.arraydict import ArrayDict
from config import config
from unilibs.baseplot import BasePlot


class AlphasSensitivityPlot(BasePlot):

    def __init__(self, measurements=None, **kwargs):
        super(AlphasSensitivityPlot, self).__init__(**kwargs)
        self.ax = self.fig.add_subplot(111)
        self.measurements = measurements
        self.prepare()
        self.set_style(self.ax, style='cmsprel')

    def prepare(self):

        minorlocator = MultipleLocator(0.1)
        self.ax.yaxis.set_minor_locator(minorlocator)
        self.ax.xaxis.set_minor_formatter(
            plt.FuncFormatter(self.log_locator_filter))

        bin_down = self.measurements[0].get_source('y_low')()[0]
        bin_up = self.measurements[0].get_source('y_high')()[0]
        if bin_down != 0.:
            ybin_label = "${0} \leq |y| < {1}$".format(bin_down, bin_up)
        else:
            ybin_label = "$|y| < {0}$".format(bin_up)

        self.ax.text(0.02, 0.85, ybin_label, va='bottom',
                     ha='left', transform=self.ax.transAxes, color='black')

        self.ax.set_xscale('log')

    def produce(self):

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

    def finalize(self):
        self._save_fig()
        plt.close(self.fig)


class DataTheoryRatio(BasePlot):

    def __init__(self, measurements=None, **kwargs):
        super(DataTheoryRatio, self).__init__(**kwargs)
        self.ax = self.fig.add_subplot(111)

        self.measurements = measurements
        self.prepare()

    def prepare(self):
        self.ax.set_xscale('log')
        minorlocator = MultipleLocator(0.1)
        self.ax.yaxis.set_minor_locator(minorlocator)
        self.ax.xaxis.set_minor_formatter(
            plt.FuncFormatter(self.log_locator_filter))

        self.ax.tick_params(which='major', length=8, width=1.5)
        self.ax.tick_params(which='minor', length=4, width=1)
        self.ax.yaxis.grid(True)

        bin_down = self.measurements[0].get_source('y_low')()[0]
        bin_up = self.measurements[0].get_source('y_high')()[0]
        if bin_down != 0.:
            ybin_label = "${0} \leq |y| < {1}$".format(bin_down, bin_up)
        else:
            ybin_label = "$|y| < {0}$".format(bin_up)

        self.set_style(self.ax, style='cmsprel')
        self.ax.text(0.02, 0.85, ybin_label, va='bottom',
                     ha='left', transform=self.ax.transAxes, color='black')

    def produce(self):

        ref_measurement = self.measurements[0]
        exp_unc = ref_measurement.get_diagonal_unc(origin=('exp',))
        stat_unc = ref_measurement.get_diagonal_unc(label=('stat',))
        print "hallo"
        print stat_unc
        theo_unc = ref_measurement.get_diagonal_unc(origin=('theo',))

        self.ax.axhline(y=1.0, lw=2.0, color='black', zorder=0)

        self.ax.errorbar(x=ref_measurement.get_bin_mid('pt'),
                         xerr=ref_measurement.get_bin_error('pt'),
                         y=ref_measurement.data / ref_measurement.theory,
                         yerr=stat_unc / ref_measurement.theory,
                         fmt='o',
                         capthick=2,
                         color='black',
                         label='Data + Stat.')

        self.ax.fill_between(
            x=self.steppify_bin(ref_measurement.get_bin('pt').T, isx=True),
            y1=self.steppify_bin((ref_measurement.data - exp_unc[
                0]) / ref_measurement.theory, isx=False),
            y2=self.steppify_bin((ref_measurement.data + exp_unc[
                1]) / ref_measurement.theory, isx=False),
            hatch='x', alpha=1.0, color='none',
            edgecolor='Gold')

        p = matplotlib.patches.Rectangle((1, 1), 0, 0,
                                         label='Sys.',
                                         hatch='x', alpha=1.0, fill=False,
                                         edgecolor='Gold')
        self.ax.add_patch(p)

        self.ax.text(0.02, 0.98, ref_measurement.pdf_set, va='top',
                     ha='left', transform=self.ax.transAxes, color='black')

        for measurement in self.measurements:
            color = next(self.ax._get_lines.color_cycle)
            print measurement.theory
            print measurement.get_bin('pt')
            self.ax.fill_between(
                x=self.steppify_bin(measurement.get_bin('pt').T, isx=True),
                y1=self.steppify_bin((measurement.theory - theo_unc[
                    0]) / ref_measurement.theory, isx=False),
                y2=self.steppify_bin((measurement.theory + theo_unc[
                    1]) / ref_measurement.theory, isx=False),
                hatch='//', alpha=1.0, color='none',
                edgecolor=color)

            #self.ax.plot(self.steppify_bin(ref_measurement.get_bin('pt').T,
                                           #isx=True),
                         #self.steppify_bin(measurement.theory /
                                           #ref_measurement.theory),
                         #color=color, linestyle='-', linewidth=2)

            p = matplotlib.patches.Rectangle((1, 1), 0, 0,
                                             label=measurement.pdf_set,
                                             hatch='//', alpha=1.0, fill=False,
                                             edgecolor=color)
            self.ax.add_patch(p)

        self.ax.set_xlabel(r'$p_\mathrm{T}$ (GeV)')
        self.ax.set_ylabel('Ratio to {0}'.format(ref_measurement.pdf_set))
        self.ax.set_ylim(0.5,1.5)
        self.ax.legend(loc='upper right')

    def finalize(self):
        self._save_fig()
        plt.close(self.fig)


class Chi2Distribution(BasePlot):

    def __init__(self, analysis, pdf_family, scenario, scale, **kwargs):
        super(Chi2Distribution, self).__init__(**kwargs)
        self.ax = self.fig.add_subplot(111)

        self.prepare()

        cache_filepath = os.path.join(config.cache_chi2, analysis,
                                      '{}_{}_{}.npz'.format(pdf_family,
                                                            scenario,
                                                            scale))
        self.data = ArrayDict(cache_filepath)
        self.pdf_family = pdf_family
        self.analysis = analysis
        self.scale = scale

    def prepare(self):
        self.set_style(self.ax, style='cmsprel')

    def produce(self):

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

    def finalize(self):
        self._save_fig()
        plt.close(self.fig)

    @staticmethod
    def fit_polynomial(data, deg=2):

        poly = Polynomial.fit(data['alphas'], data['chi2'], deg)
        if np.isnan(np.min(poly.coef)):
            print 'RankWarning in fit'
            return None
        return poly

    @staticmethod
    def extract_voi(poly, data):

        poly_deriv = poly.deriv()
        voi = dict()
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


