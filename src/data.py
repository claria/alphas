import os

from config import config
from src.measurement import Source, UncertaintySource
from src.libs import arraydict


class DataFile(object):

    def __init__(self, analysis):

        self._ana_config = config.get_config(analysis)
        self._data_file = os.path.join(config.data_dir, analysis + '.npz')

        self._array_dict = arraydict.ArrayDict(self._data_file)
        self.sources = {}

        self.analyze_arraydict()


    def analyze_arraydict(self):
        for label, item in self._array_dict.items():
            if not label in self._ana_config['data_description']:
                continue
            
            origin = self._ana_config['data_description'][label]
            if origin in ['bin','corr', 'data', 'theory']:
                self.sources[label] = Source(label=label, array=item, origin=origin)
                    
            elif origin in ['exp_uncert', 'theo_uncert']:
                self.sources[label] = UncertaintySource(origin= origin,
                                                    array=item,
                                                    label= label, 
                                                    corr_type = 'uncorr'
                                                    )