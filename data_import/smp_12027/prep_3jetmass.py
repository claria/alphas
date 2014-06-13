#! /usr/bin/env python2
import sys
import numpy as np
import numpy

def cropData(data, xlim = None):
  def cropData2(data, mask):
    if not mask.any():
      return data
    tmp = dict(data)
    for key in data:
      try:
        if data[key].ndim == 1:
          tmp[key] = numpy.array(numpy.ma.masked_array(data[key],mask).compressed())
        elif (data[key].ndim == 2) and (data[key].shape[0] == 2):
          tmp[key] = numpy.array([
            numpy.ma.masked_array(data[key][0], mask).compressed(),
            numpy.ma.masked_array(data[key][1], mask).compressed()])
        elif (data[key].ndim == 2) and (data[key].shape[0] == data[key].shape[1]):
          tmp[key] = numpy.array(numpy.ma.compress_rowcols(
            numpy.ma.masked_array(data[key], numpy.outer(mask, mask))))
      except:
        pass
    return tmp
  return cropData2(data, numpy.ma.masked_outside(data['x'], *xlim).mask)

def main():
    npz_file = cropData(np.load("getData_all_vm3_b_AK7_yb0_1_yb1_2_jr=PF_trigger=all_run=2011all.npz"), (445,3270))
    npz_npcorr_file = cropData(np.load("getNLO_np_fit_vm3_b_AK7_yb0_1_yb1_2_gen=None_np_sh=_np_py=.npz"), (445,3270))

    out = {}

    # print npz_file.files

    out['npcor'] = npz_npcorr_file['y']
    out['xs'] = npz_file['y']

    out['RelativeJERHF']   = npz_file['ye_tssc_RelativeJERHF']  
    out['cov_RelativeJERHF']   = npz_file['cov_tssc_RelativeJERHF']  

    out['RelativeJEREC2']  = npz_file['ye_tssc_RelativeJEREC2'] 
    out['cov_RelativeJEREC2']  = npz_file['cov_tssc_RelativeJEREC2'] 

    out['RelativeJEREC1']  = npz_file['ye_tssc_RelativeJEREC1'] 
    out['cov_RelativeJEREC1']  = npz_file['cov_tssc_RelativeJEREC1'] 

    out['RelativeStatEC2'] = npz_file['ye_tssc_RelativeStatEC2']
    out['cov_RelativeStatEC2'] = npz_file['cov_tssc_RelativeStatEC2']

    out['PileUpJetRate']   = npz_file['ye_tssc_PileUpJetRate']  
    out['cov_PileUpJetRate']   = npz_file['cov_tssc_PileUpJetRate']  

    out['PileUpBias']      = npz_file['ye_tssc_PileUpBias']     
    out['cov_PileUpBias']      = npz_file['cov_tssc_PileUpBias']     

    out['RelativeFSR']     = npz_file['ye_tssc_RelativeFSR']    
    out['cov_RelativeFSR']     = npz_file['cov_tssc_RelativeFSR']    

    out['PileUpDataMC']    = npz_file['ye_tssc_PileUpDataMC']   
    out['cov_PileUpDataMC']    = npz_file['cov_tssc_PileUpDataMC']   

    out['PileUpOOT']       = npz_file['ye_tssc_PileUpOOT']      
    out['cov_PileUpOOT']       = npz_file['cov_tssc_PileUpOOT']      

    out['Time']            = npz_file['ye_tssc_Time']           
    out['cov_Time']            = npz_file['cov_tssc_Time']           

    out['HighPtExtra']     = npz_file['ye_tssc_HighPtExtra']    
    out['cov_HighPtExtra']     = npz_file['cov_tssc_HighPtExtra']    

    out['Flavor']          = npz_file['ye_tssc_Flavor']         
    out['cov_Flavor']          = npz_file['cov_tssc_Flavor']         

    out['PileUpPt']        = npz_file['ye_tssc_PileUpPt']       
    out['cov_PileUpPt']        = npz_file['cov_tssc_PileUpPt']       

    out['SinglePion_ys']   = npz_file['ye_tssc_SinglePion_ys']  
    out['cov_SinglePion_ys']   = npz_file['cov_tssc_SinglePion_ys']  

    out['RelativeStatHF']  = npz_file['ye_tssc_RelativeStatHF'] 
    out['cov_RelativeStatHF']  = npz_file['cov_tssc_RelativeStatHF'] 

    out['Absolute']        = npz_file['ye_tssc_Absolute']       
    out['cov_Absolute']        = npz_file['cov_tssc_Absolute']       

    out['stat']                 = npz_file['ye_stat']                
    out['cov_stat']                 = npz_file['cov_stat']                

    out['unf']                  = npz_file['ye_unf']                 
    out['cov_unf']                  = npz_file['cov_unf']                 

    out['lumi']                 = npz_file['ye_lumi']                
    out['cov_lumi']                 = npz_file['cov_lumi']                


    out['uc']                   = npz_file['ye_uc']                  
    out['cov_uc']                   = npz_file['cov_uc']                  
    
    
    out['m3']                   = npz_file['x']                  

    print out['m3'].size
    np.savez('../../data/smp12027.npz', **out)


if __name__ == '__main__':
    main()
