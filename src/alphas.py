from src.measurement import Measurement
from src.providers import DataProvider, TheoryProvider
from src.chi2 import Chi2Cov, Chi2Nuisance
from config import config


def perform_chi2test(analysis, pdf_family):

	data = DataProvider('qcd11004v2')
	
	lhapdf_config = config.get_config('lhapdf')
	ana_config = config.get_config(analysis)

	for pdf_set in lhapdf_config[pdf_family]:
		print pdf_set
		for scale in ana_config['theory'].as_list('scales'):
			theo = TheoryProvider(analysis, pdf_family, pdf_set, scale)
			print scale
