import sys
import numpy

from fastnloreader import FastNLOLHAPDF
#from fastnloreader import SetGlobalVerbosity


class Fnlo(object):
    def __init__(self, table_filename, lhgrid_filename, member=0,
                 scale_factor=(1.0, 1.0), pdf_type=None):

        self._table_filename = table_filename
        self._lhgrid_filename = lhgrid_filename

        self._member = member
        self._scale_factor = scale_factor

        if pdf_type is None:
            self._identify_pdf()
        else:
            self._pdf_type = pdf_type



        # FastNLOReader instance
        #SetGlobalVerbosity(1)
        self._fnlo = FastNLOLHAPDF(self._table_filename,
                                   self._lhgrid_filename, self._member)
        self._fnlo.FillPDFCache()
        self._fnlo.SetScaleFactorsMuRMuF(*self._scale_factor)
        self._fnlo.SetLHAPDFMember(self._member)

        # infos about pdfs and bins
        self._npdfmembers = self._fnlo.GetNPDFMembers()
        self._nobsbins = self._fnlo.GetNObsBins()
        self._ndiffbins = self._fnlo.GetNDiffBin()

        #Get Differential Bins
        self._bins_down = numpy.array(self._fnlo.GetLowBinEdge()).transpose()
        self._bins_up = numpy.array(self._fnlo.GetUpBinEdge()).transpose()

        #Member Cross Sections
        self._member_crosssections = None
        #self._xslo = None
        #self._xsnlo = None
        #self._pdf_uncert = None
        #self._pdf_cov_matrix = None

    def __del__(self):
        del self._fnlo

    def _identify_pdf(self):
        """ Identify type of PDF LHgrid file
        MC: Monte carlo ensemble with replicas
        EV: Asymmetric Eigenvectors
        SEV: Symmetric Eigenvectors
        EVVAR: Asymmetric Eigenvectors with additional VAR PDF
        """
        # Scale PDF self._clscale
        self._clscale = 1.00
        if self._lhgrid_filename.startswith('CT10'):
            self._pdf_type = 'EV'
            self._clscale = 1.645
        elif self._lhgrid_filename.startswith('MSTW'):
            self._pdf_type = 'EV'
        elif self._lhgrid_filename.startswith('NNPDF'):
            self._pdf_type = 'MC'
        elif self._lhgrid_filename.startswith('HERAMC'):
            self._pdf_type = 'MC'
        elif self._lhgrid_filename.startswith('HERA'):
            self._pdf_type = 'EVVAR'
        elif self._lhgrid_filename.startswith('ABM'):
            self._pdf_type = 'SEV'
        else:
            raise Exception("PDF type not identified:{}".format(self._lhgrid_filename))
            #
            # Overview functions
            #
    def get_all(self):
        results = {}
        results['xsnlo'] = self.get_central_crosssection()
        results['pdf_uncert'] = self.get_pdf_uncert()
        results['cov_pdf_uncert'] = self.get_pdf_cov_matrix()
        results['scale_uncert'] = self.get_scale_uncert()
        return results

    def get_central_crosssection(self):
        if self._pdf_type == 'MC':
            return self.get_mean_crosssection()
        elif self._pdf_type in ['EV', 'SEV', 'EVVAR', 'NONE']:
            return self.get_member_crosssection(member=0)
        else:
            raise Exception("PDF type not identified:{}".format(self._pdf_type))
    def get_bins_up(self):
        return self._bins_up

    def get_bins_down(self):
        return self._bins_down

    def get_member_crosssections(self):
        if self._member_crosssections is None:
            self._calc_member_crosssections()
        return self._member_crosssections

    def get_member_crosssection(self, member=None, scale_factor=None):
        if scale_factor is None:
            scale_factor = self._scale_factor
        if member is None:
            if self._member is None:
                print "No valid member"
                sys.exit(1)
            else:
                member = self._member

        self._fnlo.SetScaleFactorsMuRMuF(*scale_factor)
        self._fnlo.SetLHAPDFMember(member)
        self._fnlo.CalcCrossSection()
        return numpy.array(self._fnlo.GetCrossSection())

    #
    #   Internal Functions
    #
    def _calc_member_crosssections(self):
        """Read Cross Section for all members in PDF"""

        self._member_crosssections = numpy.zeros((self._npdfmembers,
                                                  self._nobsbins))

        for member in range(0, self._npdfmembers):
            #self._fnlo.SetLHAPDFMember(member)
            #self._fnlo.CalcCrossSection()
            self._member_crosssections[member] = self.get_member_crosssection(
                member=member)


            def get_cross_section(self, member=None, scale_factor=None):
                if scale_factor:
                    self._scale_factor = scale_factor
        if self._pdf_type == 'MC':
            return self.get_mean_crosssection()
        elif self._pdf_type in ['EV', 'SEV']:
            return self.get_member_crosssection(member=member)

    def get_mean_crosssection(self, ):
        if self._member_crosssections is None:
            self._calc_member_crosssections()
        return numpy.mean(self._member_crosssections[1:], axis=0)

    def get_pdf_std(self, ):
        if self._member_crosssections is None:
            self._calc_member_crosssections()
        std = numpy.std(self._member_crosssections[1:], axis=0)
        return numpy.vstack((std, std))

    def get_pdf_ev(self, symmetric=False):
        if self._member_crosssections is None:
            self._calc_member_crosssections()
        pdf_uncert = numpy.zeros((2, self._nobsbins))
        print "npdfmembers", self._npdfmembers
        if symmetric is False:
            for i in range(1, self._npdfmembers / 2 + 1):
                pdf_uncert[0] += numpy.square(numpy.minimum(numpy.minimum(
                    self._member_crosssections[2 * i - 1] -
                    self._member_crosssections[0],
                    self._member_crosssections[2 * i] -
                    self._member_crosssections[0]),
                                                            0.))
                pdf_uncert[1] += numpy.square(numpy.maximum(numpy.maximum(
                    self._member_crosssections[2 * i - 1] -
                    self._member_crosssections[0],
                    self._member_crosssections[2 * i] -
                    self._member_crosssections[0]),
                                                            0.))
            pdf_uncert = numpy.sqrt(pdf_uncert)
        elif symmetric is True:
            for i in range(1, self._npdfmembers / 2 + 1):
                pdf_uncert[0] += numpy.square(
                    self._member_crosssections[2 * i - 1] -
                    self._member_crosssections[2 * i])
            pdf_uncert[0] = 0.5 * numpy.sqrt(pdf_uncert[0])
            pdf_uncert[1] = pdf_uncert[0]
        return pdf_uncert

    def get_pdf_uncert(self, symmetric=False):
        if self._pdf_type == 'MC':
            return self.get_pdf_std()
        elif self._pdf_type == 'EV':
            return self.get_pdf_ev(symmetric=symmetric)
        elif self._pdf_type == 'SEV':
            print "not implemented"
            return self.get_pdf_ev(symmetric=True)
        else:
            return None

    def get_pdf_cov_matrix(self):
        if self._pdf_type == 'MC':
            return self.get_pdf_sample_covariance()
        elif self._pdf_type in ['EV', 'SEV', 'EVVAR']:
            return self.get_pdf_ev_covariance()
        else:
            return None


    def get_pdf_sample_covariance(self):
        if self._member_crosssections is None:
            self._calc_member_crosssections()
        return numpy.cov(self._member_crosssections[1:], rowvar=0)

    def get_pdf_ev_covariance(self):

        cov_matrix = numpy.zeros((self._nobsbins, self._nobsbins))
        if self._member_crosssections is None:
            self._calc_member_crosssections()
        for i in range(1, (self._npdfmembers / 2) + 1):
            cov_matrix += (numpy.matrix(self._member_crosssections[2 * i] -
                    self._member_crosssections[
                    2 * i - 1]).getT() * numpy.matrix(
                self._member_crosssections[2 * i] -
                self._member_crosssections[2 * i - 1]))

        cov_matrix /= 4.
        return cov_matrix


    def get_scale_uncert(self, var='6p', def_scale_factor=(1.0, 1.0)):
        if var == '6p':
            scale_factors = [(1.0, 2.0), (1.0, 0.5), (2.0, 1.0),
                             (2.0, 2.0), (0.5, 0.5), (0.5, 1.0)]
        elif var == '2p':
            scale_factors = [(2.0, 2.0), (0.5, 0.5)]
        else:
            scale_factors = []

        def_crosssection = self.get_member_crosssection(
            scale_factor=def_scale_factor)
        scale_uncert = numpy.zeros((2, self._nobsbins))

        for scale_factor in scale_factors:
            scale_crosssection = self.get_member_crosssection(
                scale_factor=scale_factor)
            scale_uncert[0] = numpy.maximum(scale_uncert[0],
                                            def_crosssection - scale_crosssection)

            scale_uncert[1] = numpy.maximum(scale_uncert[1],
                                            scale_crosssection - def_crosssection)

        return scale_uncert
