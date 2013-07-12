import numpy

class Measurement(object):

    def __init__(self, data=None, theory=None, uncertainties=None, bins=None):

        self._theory = self.set_theory(theory)
        self._data = self.set_data(data)

        if uncertainties is None:
            self._uncertainties = []
        if bins is None:
            self._bins = []
        
        self._mask = None
        self._nbins = None

    def set_theory(self, theory):
        self._theory = theory
        if theory is not None:
            self._nbins = theory.array.size

    def get_theory(self):
        return self._theory

    theory = property(get_theory, set_theory)

    def set_data(self, data):
        self._data = data
        if data is not None:
            self._nbins = data.array.size

    def get_data(self):
        return self._data
    data = property(get_data, set_data)
    
    def add_sources(self, sources):
        for source in sources:
            print source.label
            if source.origin == 'data':
                self.data = source
            elif source.origin == 'theory':
                self.theory = source
            elif source.origin == 'bin':
                self._bins.append(source)
            else:
                self._uncertainties.append(source)
    
    def add_uncertainty_source(self, uncertainty):
        self._uncertainties.append(uncertainty)

#     def get_covariance_matrix(self, origin=None, corr_type=None):
#         _cov_matrix = numpy.zeros((self._nbins,self._nbins))
#         for source in self._uncertainties:
#             if source.origin is None or uncertainty.origin == origin:
#                 if corr_type is None or uncertainty.corr_type == corr_type:
#                     _cov_matrix += uncertainty.get_cov_matrix()
#         return _cov_matrix

#    def get_total_cov_matrix(self):
#        _cov_matrix = numpy.zeros((self._nbins,self._nbins))
#        for label, uncertainty in self._uncertainties.items():
#            _cov_matrix += uncertainty.get_cov_matrix()
#        return _cov_matrix
#
#    def get_experimental_cov_matrix(self):
#        _cov_matrix = numpy.zeros((self._nbins,self._nbins))
#        for uncertainty in self._uncertainties:
#            if uncertainty.origin == 'exp':
#                _cov_matrix += uncertainty.get_cov_matrix()
#
#    def get_theoretical_cov_matrix(self):
#        _cov_matrix = numpy.zeros((self._nbins,self._nbins))
#        for uncertainty in self._uncertainties:
#            if uncertainty.origin == 'exp':
#                _cov_matrix += uncertainty.get_cov_matrix()


#     def get_dic_of_abs_uncertainties(self, corr_type='', symmetric=False):
#         uncert_dic = {}
#         print self._uncertainties
#         for label, uncertainty in self._uncertainties.items():
#             print uncertainty.corr_type
#             if uncertainty.corr_type == corr_type:
#                 uncert_dic[label] = uncertainty.get_absolute_uncertainty(symmetric=symmetric)
#         return uncert_dic

    def mask_data(self, mask):
        self._mask = mask
    def unmask_data(self):
        self._mask = None
    
    def get_obs(self, label):
        """Return Observable of given label"""
        if label == 'data':
            return self.data
        elif label == 'theory':
            return self.theory
        elif label in self._bins:
            return self._bins[label]
        elif label in self._uncertainties:
            return self._uncertainties[label]
        else:
            #Label not found
            return None


    def apply_cut(self, obs_label, comp_operator, value):
        """obs must be data,theory,binlabel, uncertlabel
        and condition on the following form ==, !=, <=, < """
        comp_operators = ['<', '>', '==', '>=', '<=', '!=']
        obs = self.get_obs(obs_label) 
        if comp_operator == '<':
            self._mask = obs < value 
        elif comp_operator == '>':
            self._mask = obs > value 
        elif comp_operator == '==':
            self._mask = obs == value 
        elif comp_operator == '>=':
            self._mask = obs >= value 
        elif comp_operator == '<=':
            self._mask = obs <= value 
        elif comp_operator == '!=':
            self._mask = obs != value 
        else:
            self._mask = None

class Source(object):

    def __init__(self, array=None, label=None, origin=None, ):
        self._label = label
        self._array = array
        self._origin = origin
        self._nbins = array.shape[0]

    def get_nbins(self):
        return self._nbins
    nbins = property(get_nbins)

    def get_array(self):
        return self._array
    array = property(get_array)

    def get_origin(self):
        return self._origin
    origin = property(get_origin)

    def get_label(self):
        return self._label
    label = property(get_label)


class UncertaintySource(Source):

    def __init__(self, array=None, label=None, origin=None, cov_matrix=None,
                corr_type=None, multiplicative=False):
                    
        super(UncertaintySource, self).__init__(array=array, label=label, origin=origin)
        
        
        if array.ndim == 1:
            self._symmetric = True
            self._nbins = array.shape[0]
        elif array.ndim ==2:
            self._symmetric = False
            self._nbins = array.shape[1]
        
        self._abs_uncert = array
        self._corr_type = corr_type
        self._corr_matrix = None
        self._cov_matrix = cov_matrix
        self._multiplicative = multiplicative

        
        if cov_matrix is not None:
            self._symmetric = True
            # calculate abs uncert

    def set_absolute_uncertainty(self, abs_uncert, symmetric=False):
        if abs_uncert.ndim == 1:
            #Symmetric uncertainty
            self._sym_uncert = abs_uncert
            self._abs_uncert = numpy.array((abs_uncert,abs_uncert))
        elif abs_uncert.ndim == 2:
            #Assume it is asymmetric
            self._abs_uncert = abs_uncert
        self._nbins = self._abs_uncert.shape[1]
        self._symmetric = symmetric

    def get_absolute_uncertainty(self, symmetric=False):
        if symmetric == True:
            return self._sym_uncert
        else:
            return self._abs_uncert

    abs_uncert = property(get_absolute_uncertainty, set_absolute_uncertainty)

    def set_relative_uncertainty(self, rel_uncert, ref, symmetric=False):
        self._abs_uncert = rel_uncert * ref
        self._nbins = self._abs_uncert.shape[1]
        self._symmetric = symmetric

    def get_relative_uncertainty(self, ref, symmetric=False):
        if symmetric == True:
            return self._sym_uncert / ref
        else:
            return self._abs_uncert / ref

    def set_cov_matrix(self, cov_matrix):
        self._cov_matrix = cov_matrix
        self._nbins = self._cov_matrix.shape[0]
        self._abs_uncert = numpy.array((cov_matrix.diagonal(),
                                    cov_matrix.diagonal()))
        self._sym_uncert = cov_matrix.diagonal()

    def get_cov_matrix(self):
        if self._cov_matrix is not None:
            return self._cov_matrix
        else:
            self._calc_cov_matrix()
            return self._cov_matrix
    
    cov_matrix = property(get_cov_matrix, set_cov_matrix)

    def set_correlation_matrix(self, corr_matrix):
        self._corr_type = 'custom'
        self._corr_matrix = corr_matrix
        self._calc_cov_matrix()

    def get_correlation_matrix(self):
        if self._corr_matrix is not None:
            return self._corr_matrix
        else:
            self._calc_correlation_matrix()
            return self._corr_matrix

    corr_matrix = property(get_correlation_matrix, set_correlation_matrix)

    def _calc_correlation_matrix(self):
        if self._corr_type == 'fully':
            self._corr_matrix = numpy.ones((self._nbins,self._nbins))
        elif self._corr_type == 'uncorr':
            self._corr_matrix = numpy.identity(self._nbins)
        else:
            pass
            # in case of custom, corr matrix should already be filled


    def set_corr_type(self, corr_type):
        self._corr_type = corr_type
        # This affects correlation matrices and covariance martrices
        self._calc_cov_matrix()
        self._calc_correlation_matrix()
    def get_corr_type(self):
        return self._corr_type
        
    corr_type = property(get_corr_type, set_corr_type)

    def set_label(self, label):
        self._label = label
    def get_label(self):
        return self._label
        
    label = property(get_label, set_label)



    def get_origin(self):
        return self._origin
    def set_origin(self,origin):
        self._origin = origin
        
    origin = property(get_origin, set_origin)


    def _calc_cov_matrix(self):
        if self._sym_uncert is None:
            pass
            #self._symmetrize()
        if self._corr_type == 'fully':
            self._cov_matrix = numpy.outer(self._sym_uncert, 
                                            self._sym_uncert)
        elif self._corr_type == 'uncorr':
            self._cov_matrix = numpy.diagflat(
                                        numpy.square(self._sym_uncert))
        else:
            self._cov_matrix = (self._sym_uncert * self._corr_matrix * 
                                                            self._sym_uncert)

#     def _symmetrize(self):
#         """Symmetrize uncertainty of shape (2,xxx)"""
#         self._sym_uncert = 0.5 * (self._uncert[0] + self._uncert[1])
