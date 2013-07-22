from src.measurement import Measurement
from src.providers import DataProvider, TheoryProvider
from src.chi2 import Chi2Cov, Chi2Nuisance
from config import config
from src.libs.arraydict import ArrayDict
import numpy
import os


def get_measurement(analysis, pdf_set, scale, scenario='all',  *args, **kwargs):

    data = DataProvider(analysis)
    theo = TheoryProvider(analysis, pdf_set, scale)
    meas = Measurement(sources=theo.sources + data.sources,
                       scenario=scenario,
                       pdf_set=pdf_set,
                       analysis=analysis)

    return meas

def perform_chi2test(*args, **kwargs):

    lhapdf_config = config.get_config('lhapdf2')
    ana_config = config.get_config(kwargs['analysis'])

    kwargs['pdf_sets'] += lhapdf_config['pdf_families'][kwargs['pdf_family']]

    scenario = ana_config['scenarios'].get(kwargs['scenario'], None)
    #Create Result array
    for scale in ana_config['theory'].as_list('scales'):

        npdf_sets = len(kwargs['pdf_sets'])
        results = ArrayDict(**{'alphas' : numpy.zeros(npdf_sets),
                               'chi2' : numpy.zeros(npdf_sets)})

        cache_filepath = os.path.join(config.cache_chi2,
                                            kwargs['analysis'],
                                            '{}_{}.npz'.format(
                                            kwargs['pdf_family'], scale))
        for i, pdf_set in enumerate(kwargs['pdf_sets']):
            #print "Running over PDFset", pdf_set
            meas = get_measurement(kwargs['analysis'], pdf_set, scale, scenario=scenario)
            alphas = float(lhapdf_config['pdf_sets'][pdf_set]['alphas'])
            chi2cov = Chi2Cov(meas)
            print chi2cov.get_chi2()
            #chi2nuis = Chi2Nuisance(meas)
            #print chi2nuis.get_chi2()
            results['alphas'][i] = alphas
            results['chi2'][i] = chi2cov.get_chi2()
        results.save(filename=cache_filepath)
        print results





