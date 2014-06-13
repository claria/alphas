import os

from libs import arraydict
from measurement import Source, UncertaintySource
from fnlo import fastNLOUncertainties
from abc import ABCMeta
from config import config


class Provider(object):

    def __init__(self):
        __metaclass__ = ABCMeta
        self.sources = []
        self._array_dict = None

    def parse_arraydict(self):
        for label, item in self._array_dict.items():
            if not label in self._ana_config['data_description']:
                continue

            origin = self._ana_config['data_description'][label]
            if origin in ['bin', 'data_correction', 'theo_correction', 'data', 'theory']:
                source = Source(label=label, arr=item, origin=origin)
                self.sources.append(source)
            elif origin in ['exp_uncert', 'theo_uncert']:
                corr_type = self._ana_config['corr_type'][label]
                error_scaling = self._ana_config['error_scaling'].get(label,
                                                                      'none')
                if corr_type in ['fully', 'uncorr']:
                    uncertainty_source = UncertaintySource(origin=origin,
                                                           arr=item,
                                                           label=label,
                                                           corr_type=corr_type,
                                                           error_scaling=error_scaling)
                elif corr_type == 'bintobin':
                    if 'cov_' + label in self._array_dict:
                        uncertainty_source = UncertaintySource(origin=origin,
                                                               cov_matrix=self._array_dict[
                                                                   'cov_' + label],
                                                               label=label,
                                                               corr_type=corr_type,
                                                               error_scaling=error_scaling)
                    elif 'cor_' + label in self._array_dict:
                        uncertainty_source = UncertaintySource(origin=origin,
                                                               arr=item,
                                                               corr_matrix=
                                                               self._array_dict[
                                                                   'cor_' + label],
                                                               label=label,
                                                               corr_type=corr_type,
                                                               error_scaling=error_scaling)
                self.sources.append(uncertainty_source)
            else:
                print "Omitting unknown source {} of origin {}.".format(label, origin)


class DataProvider(Provider):

    def __init__(self, analysis):
        super(DataProvider, self).__init__()
        self._ana_config = config.get_config(analysis)
        self._data_file = os.path.join(config.data_dir, analysis + '.npz')

        self._array_dict = arraydict.ArrayDict(self._data_file)

        self.parse_arraydict()


class TheoryProvider(Provider):

    def __init__(self, analysis, pdf_set, scale):

        super(TheoryProvider, self).__init__()
        self._analysis = analysis
        self._pdf_set = pdf_set
        self._scale = [float(item) / 10. for item in scale.split('_')]
        self._ana_config = config.get_config(analysis)
        self._table = self._ana_config['theory']['table']
        self._table_filepath = os.path.join(config.table_dir,
                                            self._ana_config['theory'][
                                                'table'] + '.tab')

        self._lhapdf_config = config.get_config('lhapdf2')['pdf_sets'][pdf_set]
        self._lhgrid_filename = self._lhapdf_config['lhgrid_file']

        # scale_str = '_'.join(str(x).replace('.','') for x in scale)
        self._cache_filepath = os.path.join(config.cache_theory,
                                            self._table,
                                            '{}_{}.npz'.format(pdf_set, scale))

        self._array_dict = None

        self._read_cached()

    def _read_cached(self):
        if os.path.exists(self._cache_filepath):
            self._array_dict = arraydict.ArrayDict(self._cache_filepath)
            self.parse_arraydict()

        else:
            self._cache_theory()
            self.parse_arraydict()

    def _cache_theory(self):
        fnloreader = fastNLOUncertainties(self._table_filepath, self._lhgrid_filename,
                          scale_factor=self._scale,
                          errortype=self._lhapdf_config['errortype'],
                          member=int(self._lhapdf_config.get('member', 0)),
                          pdf_clscale=float(
                              self._lhapdf_config.get('pdf_clscale', 1.0)))
        self._array_dict = arraydict.ArrayDict(**fnloreader.get_all())
        del fnloreader
        self._array_dict.save(self._cache_filepath)
