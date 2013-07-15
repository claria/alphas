import numpy


class Measurement(object):

    def __init__(self, data=None, theory=None, uncertainties=None, bins=None):

        self._theory = self.set_theory(theory)
        self._data = self.set_data(data)

        if uncertainties is None:
            self._uncertainties = []
        if bins is None:
            self._bins = []

        self._corrections = []
        self._mask = None
        self._nbins = None

    def set_theory(self, theory):
        self._theory = theory
        if theory is not None:
            self._nbins = theory.array.size

    def get_theory(self):
        theory = self._theory.get_array().copy()
        for correction in self._corrections:
           theory *= correction.get_array()
        return theory

    theory = property(get_theory, set_theory)

    def set_data(self, data):
        self._data = data
        if data is not None:
            self._nbins = data.array.size

    def get_data(self):
        return self._data.get_array()

    data = property(get_data, set_data)
    
    def add_sources(self, sources):
        for source in sources:
            if source.origin == 'data':
                self.data = source
            elif source.origin == 'theory':
                self.theory = source
            elif source.origin == 'bin':
                self._bins.append(source)
            elif source.origin == 'correction':
                self._corrections.append(source)
            else:
                self._uncertainties.append(source)

    def apply_scaling(self):
        for uncertainty in self._uncertainties:
            if uncertainty.error_scaling == 'none':
                continue
            if uncertainty.error_scaling == 'linear':
                uncertainty.scale(numpy.abs(self.theory/self.data))
            elif uncertainty.error_scaling == 'poisson':
                raise Exception('Not yet implemented.')
            else:
                raise Exception('No valid error scaling')

    def add_uncertainty_source(self, uncertainty):
        self._uncertainties.append(uncertainty)

    def get_uncert_list(self, corr_type=None, origin=None, label=None):
        uncert_list = []
        for uncertainty in self._uncertainties:
            if corr_type is not None:
                if uncertainty.corr_type not in corr_type:
                    continue
            if origin is not None:
                if uncertainty.origin not in origin:
                    continue
            if label is not None:
                if uncertainty.label not in label:
                    continue
            uncert_list.append(uncertainty)
        return uncert_list


    def get_cov_matrix(self, corr_type=None, origin=None, label=None):
        cov_matrix = numpy.zeros((self._nbins,self._nbins))

        for uncertainty in self._uncertainties:
            if corr_type is not None:
                if uncertainty.corr_type not in corr_type:
                    continue
            if origin is not None:
                if uncertainty.origin not in origin:
                    continue
            if label is not None:
                if uncertainty.label not in label:
                    continue
            cov_matrix += uncertainty.get_cov_matrix()

        return cov_matrix
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
#                 uncert_dic[label] = uncertainty.get_abs_uncert(symmetric=symmetric)
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
        if self._array is not None:
            self._nbins = array.shape[0]
        else:
            self._nbins = None

    def __str__(self):
        return self._label

    def __repr__(self):
        return self._label

    def __call__(self, *args, **kwargs):
        return self.get_array()

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
                corr_matrix= None, corr_type=None, error_scaling='none'):
                    
        super(UncertaintySource, self).__init__(label=label, origin=origin)

        if cov_matrix is not None:
            self._symmetric = True
            array = numpy.sqrt(cov_matrix.diagonal())
            self._corr_matrix = cov_matrix / numpy.outer(array,array)

        self._corr_type = corr_type
        self._corr_matrix = corr_matrix
        self.error_scaling = error_scaling

        #Set Diagonal error elements
        if array.ndim == 1:
            self._symmetric = True
            self._nbins = array.shape[0]
            self._array = numpy.vstack((array,array))
        elif array.ndim ==2:
            self._symmetric = False
            self._nbins = array.shape[1]
            self._array = array

    def __call__(self, symmetric=False, *args, **kwargs):
        return self.get_array(symmetric=True)

    def set_array(self, array):
        if array.ndim == 1:
            #Symmetric uncertainty
            self._array = numpy.array((array,array))
        elif array.ndim == 2:
            #Assume it is asymmetric
            self._array = array
        self._nbins = self._array.shape[1]

    def get_array(self, symmetric=False):
        if symmetric is True:
            return self._symmetrize(self._array)
        else:
            return self._array


    # def set_relative_uncertainty(self, rel_uncert, ref, symmetric=False):
    #     self._abs_uncert = rel_uncert * ref
    #     self._nbins = self._abs_uncert.shape[1]
    #     self._symmetric = symmetric
    #
    # def get_relative_uncertainty(self, ref, symmetric=False):
    #     if symmetric == True:
    #         return self._sym_uncert / ref
    #     else:
    #         return self._abs_uncert / ref

    def set_cov_matrix(self, cov_matrix):

        array = numpy.sqrt(cov_matrix.diagonal())
        self._corr_matrix = cov_matrix / numpy.outer(array,array)
        self.set_array(array)
        self._symmetric = True

    def scale(self, scale_factor):
        self._array *= scale_factor



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

    def get_correlation_matrix(self):
        if self._corr_type == 'fully':
            return numpy.ones((self._nbins,self._nbins))
        elif self._corr_type == 'uncorr':
            return numpy.identity(self._nbins)
        elif self._corr_type == 'bintobin':
            return self._corr_matrix
        else:
            raise Exception('Correlation Type invalid.')

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

    def get_cov_matrix(self):
        if self._corr_type == 'fully':
            return numpy.outer(
                    self.get_array(symmetric=True),
                    self.get_array(symmetric=True))
        elif self._corr_type == 'uncorr':
            return numpy.diagflat(
                    numpy.square(self.get_array(symmetric=True)))
        elif self._corr_type == 'bintobin':
            return (numpy.outer(
                    self.get_array(symmetric=True),
                    self.get_array(symmetric=True)) *
                    self._corr_matrix)
        else:
            raise Exception('Correlation type not valid.')

    def _symmetrize(self, array):
        """Symmetrize uncertainty of shape (2,xxx)"""
        return 0.5 * (array[0] + array[1])
