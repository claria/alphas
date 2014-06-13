import os
import numpy

from measurement import Measurement
from providers import DataProvider, TheoryProvider
from chi2 import Chi2Nuisance, Chi2Cov
from config import config
from libs.arraydict import ArrayDict
from plotprovider import DataTheoryRatio, Chi2Distribution, AlphasSensitivityPlot


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


def batch_processing(**kwargs):
    #Get all Analyses
    analyses = ['qcd11004v2']
    #All PDF Families
    lhapdf_config = config.get_config('lhapdf2')
    pdf_families = lhapdf_config['pdf_families'].keys()

    #Remove from kwargs to avoid ambougies calling
    kwargs.pop('pdf_family')
    kwargs.pop('analysis')

    for analysis in analyses:
        ana_config = config.get_config(analysis)
        scenarios = ana_config['scenarios'].keys()
        for pdf_family in pdf_families:
            for scenario in scenarios:
                perform_chi2test(analysis,
                                 pdf_family,
                                 scenario=scenario,
                                 **kwargs)
    pass


def perform_chi2test(analysis, pdf_family, scenario='all', **kwargs):

    lhapdf_config = config.get_config('lhapdf2')
    ana_config = config.get_config(analysis)

    kwargs['pdf_sets'] += lhapdf_config['pdf_families'][pdf_family]

    scenario_uncerts = ana_config['scenarios'].get(scenario, None)

    # Create Result array
    for scale in ana_config['theory'].as_list('scales'):

        npdf_sets = len(kwargs['pdf_sets'])
        results = ArrayDict(**{'alphas': numpy.zeros(npdf_sets),
                               'chi2': numpy.zeros(npdf_sets),
                               'ndof': numpy.zeros(npdf_sets)})

        cache_filepath = os.path.join(config.cache_chi2,
                                      analysis,
                                      '{}_{}_{}.npz'.format(
                                          pdf_family,
                                          scenario, scale))
        for i, pdf_set in enumerate(kwargs['pdf_sets']):
            meas = get_measurement(analysis, pdf_set, scale,
                                   scenario=scenario_uncerts)
            #Get data mask
            mask = meas.get_mask().copy()
            for cut in ana_config['cuts']:
                cut_arr = meas.get_source(cut).get_arr()
                min_val = float(ana_config['cuts'][cut]['min'])
                max_val = float(ana_config['cuts'][cut]['max'])
                #Cut min/max of cut_obs
                cut_mask = ((cut_arr < max_val)
                                & (cut_arr >= min_val))
                mask = mask*cut_mask
            meas.set_mask(mask)

            alphas = float(lhapdf_config['pdf_sets'][pdf_set]['alphas'])
            chi2nuis = Chi2Nuisance(meas)
            results['alphas'][i] = alphas
            results['chi2'][i] = chi2nuis.get_chi2()
            results['ndof'][i] = chi2nuis.get_ndof()
            # Save nuisance parameters
            #nuisance_filename = "{}/{}_{}_{}_{}.txt".format(
            #    config.output_nuisance, analysis, pdf_set,
            #    scenario, scale)
            #chi2nuis.save_nuisance_parameters(nuisance_filename)
            print results
            print chi2nuis.get_nuisance_parameters()
        results.save(filename=cache_filepath)


def plot(analysis, **kwargs):

    lhapdf_config = config.get_config('lhapdf2')
    ana_config = config.get_config(analysis)

    if kwargs['pdf_family'] is not None:
        kwargs['pdf_sets'] += lhapdf_config['pdf_families'][
            kwargs['pdf_family']]

    for scale in ana_config['theory'].as_list('scales'):
        # Different type of plots
        if kwargs['plot'] == 'ratio':
            measurements = []
            for pdf_set in kwargs['pdf_sets']:
                measurements.append(
                    get_measurement(analysis, pdf_set, scale))

            bin1 = measurements[0].get_bin('y')
            bin1_unique = measurements[0].get_unique_bin('y')
            # b = numpy.ascontiguousarray(bin1).view(numpy.dtype((numpy.void,
            #                             bin1.dtype.itemsize * bin1.shape[1])))
            # _, idx = numpy.unique(b, return_index=True)
            # unique_a = bin1[idx]
            for bin in bin1_unique:
                mask = (bin1 == bin).T[0]
                # mask = (ylowbin == ylow)
                # Apply mask to all measurements
                map(lambda x: x.set_mask(mask), measurements)
                output_fn = '{}/ratio/{}_{}_{}_{}_{}'.format(config.output_plots,
                                                             analysis,
                                                             measurements[0].pdf_set,
                                                             scale, *bin)
                dt_plot = DataTheoryRatio(measurements, output_fn=output_fn,
                                          output_ext=['pdf', 'png'])
                dt_plot.do_plot()

        elif kwargs['plot'] == 'asratio':
            measurements = []
            for pdf_set in kwargs['pdf_sets']:
                measurements.append(
                    get_measurement(analysis, pdf_set, scale))

            # Split according the y bins
            bin1 = measurements[0].get_bin('y')
            bin1_unique = measurements[0].get_unique_bin('y')
            # b = numpy.ascontiguousarray(bin1).view(numpy.dtype((numpy.void,
            #                             bin1.dtype.itemsize * bin1.shape[1])))
            # _, idx = numpy.unique(b, return_index=True)
            # unique_a = bin1[idx]
            for bin in bin1_unique:
                mask = (bin1 == bin).T[0]
                # mask = (ylowbin == ylow)
                # Apply mask to all measurements
                map(lambda x: x.set_mask(mask), measurements)
                output_fn = '{}/asratio/{}_{}_{}_{}_{}'.format(config.output_plots,
                                                               analysis,
                                                               kwargs['pdf_family'],
                                                               scale,
                                                               *bin)
                as_plot = AlphasSensitivityPlot(measurements,
                                                output_fn=output_fn,
                                                output_ext=['pdf', ])
                as_plot.do_plot()

        elif kwargs['plot'] == 'chi2':
            output_fn = '{}/chi2/{}_{}_{}_{}.pdf'.format(
                config.output_plots,
                analysis,
                kwargs['pdf_family'],
                kwargs['scenario'],
                scale)
            chi2_plot = Chi2Distribution(analysis,
                                         kwargs['pdf_family'],
                                         kwargs['scenario'],
                                         scale,
                                         output_fn=output_fn,
                                         output_ext=['png', ])
            chi2_plot.do_plot()

