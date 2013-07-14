import numpy


class Chi2(object):

    def __init__(self, measurement = None):
        self._chi2 = 0.0
        self._measurement = measurement
        self._data = self._measurement.data
        self._theory = self._measurement.theory

    def get_chi2(self):
        self._calculate_chi2()
        return self._chi2

    def _calculate_chi2(self):
        raise NotImplementedError

class Chi2Cov(Chi2):

    def __init__(self, measurement = None):
        super(Chi2Cov,self).__init__(measurement)

    def _calculate_chi2(self):
        inv_matrix = numpy.matrix(self._measurement.get_cov_matrix()).getI()
        residual = numpy.matrix(self._data - self._theory)
        self._chi2 = (residual * inv_matrix * residual.getT())[0, 0]


class Chi2Nuisance(Chi2):

    def __init__(self, measurement):
        super(Chi2Nuisance,self).__init__(measurement)
        self._cov_matrix = self._measurement.get_cov_matrix(corr_type='bintobin')
        self._inv_matrix = numpy.matrix(self._cov_matrix).getI()
        self._beta = self._measurement.get_uncert_list(corr_type='fully')

    def _calculate_chi2(self):
        """Calculate Chi2 with different kinds of uncertainties.

        Uncorrelated uncertainties and partly correlated uncertanties are
        treated using a covariance matrix  while fully correlated
        uncertainties are treated using nuisance parameters.
        """

        chi2_corr = 0.0
        nbeta = len(self._beta)
        #npoints = len(data)
        B = numpy.zeros((nbeta,))
        A = numpy.matrix(numpy.identity(nbeta))
        #inv_matrix = cov_matrix.getI()

        #Calculate Bk and Akk' according to paper: PhysRevD.65.014012
        #Implementation similar to h1fitter
        for k in range(0, nbeta):
            B[k] = (numpy.matrix(self._data - self._theory)
                        * self._inv_matrix * numpy.matrix(self._beta[k]()).getT())
            #Better readable but much slower
            #for l in range(0,npoints):
            #    for i in range(0,npoints):
            #        B[k] += data[l] * syst_error[k][l]*
            #                (data[i]-theory[i]) * inv_matrix[l,i]
            for j in range(0, nbeta):
                A[k, j] += (numpy.matrix(self._beta[j]()) * self._inv_matrix *
                            numpy.matrix(self._beta[k]()).getT())
                #Better readable but way slower
                #for l in range(0,npoints):
                #    for i in range(0,npoints):
                #        A[k,j] += syst_error[k][i] * data[i] *
                #                 syst_error[j][l] * data[l] * inv_matrix[l,i]

        #Multiply by -1 so nuisance parameters correspond to shift
        r = numpy.linalg.solve(A, B) * (-1)
        #print r
        #Calculate theory prediction shifted by nuisance parameters
        theory_mod = self._theory.copy()
        for k in range(0, nbeta):
            theory_mod = theory_mod - r[k] * (self._beta[k]())
            chi2_corr += r[k]**2
        residual_mod = numpy.matrix(self._data - theory_mod)
        self._chi2 = (residual_mod * self._inv_matrix * residual_mod.getT())[0, 0]
        self._chi2 += chi2_corr
