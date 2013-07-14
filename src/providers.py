

import os

import numpy
from src.libs import arraydict
from src.measurement import Source, UncertaintySource
from src.fnlo import Fnlo


from config import config

class Provider(object):

    def parse_arraydict(self):
        for label, item in self._array_dict.items():
            if not label in self._ana_config['data_description']:
                continue

            origin = self._ana_config['data_description'][label]
            if origin in ['bin','correction', 'data', 'theory']:
                source = Source(label=label, array=item, origin=origin)
                self.sources.append(source)
            elif origin in ['exp', 'theo']:
                corr_type = self._ana_config['corr_type'][label]
                error_scaling = self._ana_config['error_scaling'].get(label,'none')
                if corr_type in ['fully','uncorr']:
                    uncertainty_source = UncertaintySource(origin= origin,
                                                    array=item,
                                                    label= label,
                                                    corr_type = corr_type,
                                                    error_scaling= error_scaling)
                elif corr_type == 'bintobin':
                    if 'cov_' + label in self._array_dict:
                        uncertainty_source = UncertaintySource(origin = origin,
                                    cov_matrix= self._array_dict['cov_' + label],
                                    label = label,
                                    corr_type = corr_type,
                                    error_scaling= error_scaling)
                    elif 'cor_' + label in self._array_dict:
                        uncertainty_source = UncertaintySource(origin = origin,
                                    array = item,
                                    corr_matrix=self._array_dict['cor_' + label],
                                    label = label,
                                    corr_type = corr_type,
                                    error_scaling= error_scaling)

                self.uncertainty_sources.append(uncertainty_source)


class DataProvider(Provider):

    def __init__(self, analysis):

        self._ana_config = config.get_config(analysis)
        self._data_file = os.path.join(config.data_dir, analysis + '.npz')

        self._array_dict = arraydict.ArrayDict(self._data_file)
        self.sources = []
        self.uncertainty_sources = []

        self.parse_arraydict()




class TheoryProvider(Provider):
    
    def __init__(self, analysis, pdf_family, pdf_set, scale):
        self._analysis = analysis
        self._pdf_set = pdf_set
        self._scale = scale
        self._ana_config = config.get_config(analysis)
        self._table = self._ana_config['theory']['table']
        self._table_filepath = os.path.join(config.table_dir,
                                   self._ana_config['theory']['table'] + '.tab')

        self._lhapdf_config = config.get_config('lhapdf')[pdf_family][pdf_set]

        scale_str = '_'.join(str(x).replace('.','') for x in scale)
        self._cache_filepath = os.path.join(config.cache_theory,
                self._table, pdf_family, 
                '{}_{}.npz'.format(pdf_set, scale_str))

        self._array_dict = None

        self.sources = []
        self.uncertainty_sources = []
        self._read_cached()
        
        

    def _read_cached(self):
        if os.path.exists(self._cache_filepath):
            self._array_dict = arraydict.ArrayDict(self._cache_filepath)
            self.parse_arraydict()

        else:
            self._cache_theory()
            self.parse_arraydict()

    def _cache_theory(self):

        fnloreader = Fnlo(self._table_filepath, self._pdf_set,
                            scale_factor = self._scale,
                            pdf_type=self._lhapdf_config['pdf_unc'])
        self._array_dict = arraydict.ArrayDict(**fnloreader.get_all())
        self._array_dict.save(self._cache_filepath)


# class fnlo(object):
#
#     def __init__(self, table, pdfset, member=0, scale=(1.0,1.0), pdf_unc=None):
#         self._table = os.path.join(config.table_dir, table + '.tab')
#         self._pdfset = pdfset
#         self._member = member
#         self._scale = scale
#         self._pdf_unc = pdf_unc
#         self._theory = {}
#
#         self._fnlo = FastNLOLHAPDFAdvanced(self._table, self._pdfset, self._member)
#         self._fnlo.SetScaleFactorsMuRMuF(*self._scale)
#
#         self._xsnlo = None
#         self._pdf_uncert = None
#         self._pdf_cov_matrix = None
#         self._scale_uncert_6p = None
#
#     def get_all(self):
#         theory = arraydict.ArrayDict()
#         theory['xsnlo'] = self.get_xsnlo()
#         theory['pdf_uncert'] = self.get_pdf_uncert()
#         theory['pdf_cov_matrix'] = self.get_pdf_cov_matrix()
#         theory['scale_uncert_6p'] = self.get_scale_uncert_6p()
#         return theory
#
#     def get_xsnlo(self):
#         if self._xsnlo is None:
#             self._calc_central_cross_section()
#         return self._xsnlo
#
#
#     def _calc_central_cross_section(self):
#         if self._pdf_unc == 'MC':
#             self._xsnlo = numpy.array(self._fnlo.GetMeanCrossSection())
#         else:
#             self._xsnlo = numpy.array(self._fnlo.GetMemberCrossSection(self._member))
#
#     xsnlo = property(get_xsnlo)
#
#     def get_pdf_uncert(self):
#         if self._pdf_uncert is None:
#             self._calc_pdf_uncert()
#         return self._pdf_uncert
#
#     def _calc_pdf_uncert(self):
#         if self._pdf_unc == 'MC':
#             self._pdf_uncert = numpy.array(self._fnlo.GetStdDevUncertainty())
#         elif self._pdf_unc == 'EV':
#             self._pdf_uncert = numpy.array(self._fnlo.GetEVDevUncertainty())
#         else:
#             self._pdf_uncert = None
#
#     pdf_uncert = property(get_pdf_uncert)
#
#     def get_pdf_cov_matrix(self):
#         if self._pdf_cov_matrix is None:
#             self._calc_pdf_cov_matrix()
#         return self._pdf_cov_matrix
#
#     def _calc_pdf_cov_matrix(self):
#         if self._pdf_unc == 'MC':
#             self._pdf_cov_matrix = numpy.array(self._fnlo.GetPDFSampleCovariance())
#         elif self._pdf_unc == 'EV':
#             self._pdf_cov_matrix = numpy.array(self._fnlo.GetEVCovariance())
#         else:
#             self._pdf_cov_matrix = None
#
#     pdf_cov_matrix = property(get_pdf_cov_matrix)
#
#     def get_scale_uncert_6p(self):
#         if self._scale_uncert_6p is None:
#             self._calc_scale_uncert_6p()
#         return self._scale_uncert_6p
#
#     def _calc_scale_uncert_6p(self):
#         self._scale_uncert_6p = numpy.array(self._fnlo.GetScaleUncertainty6p())
#
#     scale_uncert_6p = property(get_scale_uncert_6p)
#
#     #def get_all(self):
#         #if not self._theory:
#             #self._calc_theory()
#         #return self._theory
#
#
#     #def _calc_theory(self):
#
#         #fnlo = FastNLOLHAPDFAdvanced(self._table, self._pdfset, self._member)
#         #fnlo.SetScaleFactorsMuRMuF(*self._scale)
#
#         #if self._pdf_unc == 'MC':
#             #self._theory['xsnlo'] = numpy.array(fnlo.GetMeanCrossSection())
#             #self._theory['pdf_uncert'] = numpy.array(fnlo.GetStdDevUncertainty())
#             #self._theory['pdf_cov_matrix'] = numpy.array(fnlo.GetPDFSampleCovariance())
#         #elif self._pdf_unc == 'EV':
#             #self._theory['xsnlo'] = numpy.array(fnlo.GetMemberCrossSection(self._member))
#             #self._theory['pdf_uncert'] = numpy.array(fnlo.GetEVDevUncertainty())
#             #self._theory['pdf_cov_matrix'] = numpy.array(fnlo.GetEVCovariance())
#         #elif self._pdf_unc == 'no':
#             #self._theory['xsnlo'] = numpy.array(fnlo.GetMemberCrossSection(self._member))
#
#         #self._theory['scale_uncert_6p'] = numpy.array(fnlo.GetScaleUncertainty6p())
