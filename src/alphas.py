import os
import numpy

from src.measurement import Measurement
from src.providers import DataProvider, TheoryProvider
from src.chi2 import Chi2Cov, Chi2Nuisance
from config import config
from src.libs.arraydict import ArrayDict
from src.plotprovider import DataTheoryRatio, Chi2Distribution, AlphasSensitivityPlot


def get_measurement(analysis, pdf_set, scale, scenario='all'):
    data = DataProvider(analysis)
    theo = TheoryProvider(analysis, pdf_set, scale)
    meas = Measurement(sources=theo.sources + data.sources,
                       scenario=scenario,
                       pdf_set=pdf_set,
                       analysis=analysis,
                       pdf_config=config.get_config(
                           'lhapdf2')['pdf_sets'][pdf_set])

    return meas


def perform_chi2test(**kwargs):
    lhapdf_config = config.get_config('lhapdf2')
    ana_config = config.get_config(kwargs['analysis'])

    kwargs['pdf_sets'] += lhapdf_config['pdf_families'][kwargs['pdf_family']]

    scenario = ana_config['scenarios'].get(kwargs['scenario'], None)
    #Create Result array
    for scale in ana_config['theory'].as_list('scales'):

        npdf_sets = len(kwargs['pdf_sets'])
        results = ArrayDict(**{'alphas': numpy.zeros(npdf_sets),
                               'chi2': numpy.zeros(npdf_sets)})

        cache_filepath = os.path.join(config.cache_chi2,
                                      kwargs['analysis'],
                                      '{}_{}.npz'.format(
                                          kwargs['pdf_family'], scale))
        for i, pdf_set in enumerate(kwargs['pdf_sets']):
            #print "Running over PDFset", pdf_set
            meas = get_measurement(kwargs['analysis'], pdf_set, scale,
                                   scenario=scenario)
            alphas = float(lhapdf_config['pdf_sets'][pdf_set]['alphas'])
            chi2nuis = Chi2Nuisance(meas)
            print chi2nuis.get_chi2()
            results['alphas'][i] = alphas
            results['chi2'][i] = chi2nuis.get_chi2()
            #Save nuisance parameters
            nuisance_filename = "{}/{}_{}_{}_{}.txt".format(
                config.output_nuisance, kwargs['analysis'], pdf_set,
                kwargs['scenario'], scale)
            chi2nuis.save_nuisance_parameters(nuisance_filename)
        results.save(filename=cache_filepath)
        print results


def plot(**kwargs):

    lhapdf_config = config.get_config('lhapdf2')
    ana_config = config.get_config(kwargs['analysis'])

    if kwargs['pdf_family'] is not None:
        kwargs['pdf_sets'] += lhapdf_config['pdf_families'][
            kwargs['pdf_family']]

    for scale in ana_config['theory'].as_list('scales'):
        #Different type of plots
        if kwargs['plot'] == 'ratio':
            measurements = []
            for pdf_set in kwargs['pdf_sets']:
                measurements.append(
                    get_measurement(kwargs['analysis'], pdf_set, scale))

            #Split according the y bins
            bin1 = measurements[0].get_bin('y')
            bin1_unique = measurements[0].get_unique_bin('y')
            #b = numpy.ascontiguousarray(bin1).view(numpy.dtype((numpy.void,
            #                             bin1.dtype.itemsize * bin1.shape[1])))
            #_, idx = numpy.unique(b, return_index=True)
            #unique_a = bin1[idx]
            #print bin1
            #print unique_a
            for bin in bin1_unique:
                mask = (bin1 == bin).T[0]
                #mask = (ylowbin == ylow)
                #Apply mask to all measurements
                map(lambda x: x.set_mask(mask), measurements)
                dt_plot = DataTheoryRatio(measurements)
                dt_plot.produce_plot()
                filepath = '{}/ratio/{}_{}_{}_{}_{}.png'.\
                    format(config.output_plots, kwargs['analysis'],
                           measurements[0].pdf_set, scale, *bin)
                dt_plot.finalize(filepath=filepath)
        elif kwargs['plot'] == 'asratio':
            measurements = []
            for pdf_set in kwargs['pdf_sets']:
                measurements.append(
                    get_measurement(kwargs['analysis'], pdf_set, scale))

            #Split according the y bins
            bin1 = measurements[0].get_bin('y')
            bin1_unique = measurements[0].get_unique_bin('y')
            #b = numpy.ascontiguousarray(bin1).view(numpy.dtype((numpy.void,
            #                             bin1.dtype.itemsize * bin1.shape[1])))
            #_, idx = numpy.unique(b, return_index=True)
            #unique_a = bin1[idx]
            #print bin1
            #print unique_a
            for bin in bin1_unique:
                mask = (bin1 == bin).T[0]
                #mask = (ylowbin == ylow)
                #Apply mask to all measurements
                map(lambda x: x.set_mask(mask), measurements)
                as_plot = AlphasSensitivityPlot(measurements)
                as_plot.produce_plot()
                filepath = '{}/asratio/{}_{}_{}_{}_{}.png'.\
                    format(config.output_plots, kwargs['analysis'],
                           kwargs['pdf_family'], scale, *bin)
                as_plot.finalize(filepath=filepath)

        elif kwargs['plot'] == 'chi2':
            chi2_plot = Chi2Distribution(kwargs['analysis'],
                                         kwargs['pdf_family'], scale)
            chi2_plot.produce_plot()
            filepath = '{}/chi2/{}_{}_{}.png'.format(
                config.output_plots, kwargs['analysis'],
                kwargs['pdf_family'], scale)
            chi2_plot.finalize(filepath=filepath)