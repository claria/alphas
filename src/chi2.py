import numpy

class chi2(object):

    def __init__(self, measurement):
        self._measurement = measurement
        self._chi2 = None
        

    def _calc_chi2_nuisance(self):
        """Calculate Chi2 with different kinds of uncertainties.

        Uncorrelated uncertainties and partly correlated uncertanties are
        treated using a covariance matrix  while fully correlated
        uncertainties are treated using nuisance parameters.
        """
    
        chi2 = 0.
        chi2_corr = 0.0
        nsyst = len(syst_error)
        npoints = len(data)
        B = numpy.zeros(nsyst)
        A = numpy.matrix(numpy.identity(nsyst))
        inv_matrix = cov_matrix.getI()

        #Calculate Bk and Akk' according to paper: PhysRevD.65.014012
        #Implementation similar to h1fitter
        #TODO: systerror with theory
        for k in range(0,nsyst):
            B[k] = numpy.matrix(data-theory)*inv_matrix*numpy.matrix(
                    data*syst_error[k]).getT()
            #Better readable but much slower
            #for l in range(0,npoints):
            #    for i in range(0,npoints):
            #        B[k] += data[l] * syst_error[k][l]*
            #                (data[i]-theory[i]) * inv_matrix[l,i]
            for j in range(0,nsyst):
                A[k,j] += (numpy.matrix(syst_error[j]*data)*
                    inv_matrix * numpy.matrix(syst_error[k]*data).getT())
                #Better readable but way slower
                #for l in range(0,npoints):
                #    for i in range(0,npoints):
                #        A[k,j] += syst_error[k][i] * data[i] *
                #                 syst_error[j][l] * data[l] * inv_matrix[l,i]

        #Multiply by -1 so nuisance parameters correspond to shift
        r = numpy.linalg.solve(A,B) * (-1)
        #Calculate theory prediction shifted by nuisance parameters
        theory_mod = theory
        for k in range(0,nsyst):
            theory_mod = theory_mod - r[k]*(syst_error[k]*data)
            chi2_corr += r[k]**2
    
        chi2 = (numpy.matrix(data-theory_mod) * inv_matrix * 
                            numpy.matrix(data-theory_mod).getT())[0,0]
        chi2 += chi2_corr
    
        return (chi2, npoints, r, theory_mod)


    def _calc_chi2_covariance(self):
        """Calculate Chi2 from Covariance Matrix"""
        inv_matrix = numpy.matrix(self._measurement.get_total_cov_matrix()).getI()
        residual = numpy.matrix(self._measurement.data - self._measurement.theory)
        self._chi2 = (residual * inv_matrix * residual.getT())[0,0]
    

    def get_chi2(self, method='cov'):
        if method == 'cov':
            self._calc_chi2_covariance()
        elif method == 'nuis':
            self._calc_chi2_nuisance()
        else:
            pass
        return self._chi2
