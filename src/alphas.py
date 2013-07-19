from src.measurement import Measurement
from src.providers import DataProvider, TheoryProvider
from src.chi2 import Chi2Cov, Chi2Nuisance
from config import config


def get_measurement(analysis, pdf_set, scale, *args, **kwargs):

    data = DataProvider(analysis)
    theo = TheoryProvider(analysis, pdf_set, scale)
    meas = Measurement(sources=theo.sources + data.sources)

    return meas

def perform_chi2test(analysis, pdf_family, *args, **kwargs):


    lhapdf_config = config.get_config('lhapdf')
    ana_config = config.get_config(analysis)

    for pdf_set in lhapdf_config[pdf_family]:
        #print "Running over PDFset", pdf_set
        for scale in ana_config['theory'].as_list('scales'):
            meas = get_measurement(analysis, pdf_family, pdf_set, scale)
            mask = meas.get_source(label='ylow').get_array() == 0.0
            meas.set_mask(mask)
            chi2cov = Chi2Cov(meas)
            print chi2cov.get_chi2()
            chi2nuis = Chi2Nuisance(meas)
            print chi2nuis.get_chi2()




