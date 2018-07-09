# Program to adjust wrfHydro parameter files per output from R calibration 
# evaluations and adjustments. The following files will be adjusted:
# 1.) Fulldom.nc
# 2.) HYDRO_TBL_2D.nc
# 3.) soil_properties.nc

# Program is contingent on specific COMPLETE flag begin generated 
# from R. If this file is not created, then this program will exit
# gracefully without creating it's own COMPLETE flag. Without the 
# Python-generated COMPLETE flag, the workflow will generate an error 
# message. 

# Logan Karsten
# National Center for Atmospheric Research
# Research Applications Laboratory
# karsten@ucar.edu
# 303-497-2693

import argparse
import sys
from netCDF4 import Dataset
import os
import shutil
import pandas as pd
import time
import subprocess

def main(argv):
    # Parse arguments. Only input necessary is the run directory.
    parser = argparse.ArgumentParser(description='Main program to adjust input ' + \
             'parameters for the National Water Model')
    parser.add_argument('workDir',metavar='workDir',type=str,nargs='+',
                        help='Directory containing inputs necessary for adjustments.')
    parser.add_argument('runDir',metavar='runDir',type=str,nargs='+',
                        help='Directory containing model output where final parameter' + \
                             ' files will reside')
                        
    args = parser.parse_args()
    workDir = str(args.workDir[0])
    runDir = str(args.runDir[0])
    
    # Compose input file paths.
    fullDomOrig = workDir + "/BASELINE_PARAMETERS/Fulldom.nc"
    hydroOrig = workDir + "/BASELINE_PARAMETERS/HYDRO_TBL_2D.nc"
    soilOrig = workDir + "/BASELINE_PARAMETERS/soil_properties.nc"
    gwOrig = workDir + "/BASELINE_PARAMETERS/GWBUCKPARM.nc"
    rCompletePath = workDir + "/R_COMPLETE"
    adjTbl = workDir + "/params_new.txt"
    
    # Compose output file paths.
    fullDomOut = runDir + "/Fulldom.nc"
    hydroOut = runDir + "/HYDRO_TBL_2D.nc"
    soilOut = runDir + "/soil_properties.nc"
    gwOut = runDir + '/GWBUCKPARM.nc'
    outFlag = workDir + "/CALIB_ITER.COMPLETE"
    
    # If R COMPLETE flag not present, this implies the R code didn't run
    # to completion.
    if not os.path.isfile(rCompletePath):
        sys.exit(1)
        
    # Sleep for a few seconds in case R is still touching R_COMPLETE, or
    # from lingering parallel processes.
    time.sleep(10)
    
    os.remove(rCompletePath)
    
    # If the params_new file is not present, but the R Complete path was,
    # we are going to assume this was the last iteration and no parameters
    # need to be produced.
    if not os.path.isfile(adjTbl):
        # Touch empty COMPLETE flag file. This will be seen by workflow, demonstrating
        # calibration iteration is complete.
        try:
            open(outFlag,'a').close()
            sys.exit(0)
        except:
            sys.exit(2)
    
    try:
        shutil.copy(fullDomOrig,fullDomOut)
        shutil.copy(hydroOrig,hydroOut)
        shutil.copy(soilOrig,soilOut)
        shutil.copy(gwOrig,gwOut)
    except:
        sys.exit(3)
        
    # Read in new parameters table.
    newParams = pd.read_csv(adjTbl,sep=' ')
    paramNames = list(newParams.columns.values)
    
    # Open NetCDF parameter files for adjustment.
    idFullDom = Dataset(fullDomOut,'a')
    idSoil2D = Dataset(soilOut,'a')
    idGw = Dataset(gwOut,'a')
    idHydroTbl = Dataset(hydroOut,'a')
    
    # Loop through and adjust each parameter accordingly.
    for param in paramNames:
        if param == "bexp":
            idSoil2D.variables['bexp'][:,:,:,:] = idSoil2D.variables['bexp'][:,:,:,:]*float(newParams.bexp[0])
        
        if param == "smcmax":
            idSoil2D.variables['smcmax'][:,:,:,:] = idSoil2D.variables['smcmax'][:,:,:,:]*float(newParams.smcmax[0])
        
        if param == "slope":
            idSoil2D.variables['slope'][:,:,:] = float(newParams.slope[0])
        
        if param == "lksatfac":
            idFullDom.variables['LKSATFAC'][:,:] = float(newParams.lksatfac[0])
        
        if param == "zmax":
            idGw.variables['Zmax'][:] = float(newParams.zmax[0])
        
        if param == "expon":
            idGw.variables['Expon'][:] = float(newParams.expon[0])
        
        if param == "cwpvt":
            idSoil2D.variables['cwpvt'][:,:,:] = idSoil2D.variables['cwpvt'][:,:,:]*float(newParams.cwpvt[0])
        
        if param == "vcmx25":
            idSoil2D.variables['vcmx25'][:,:,:] = idSoil2D.variables['vcmx25'][:,:,:]*float(newParams.vcmx25[0])
        
        if param == "mp":
            idSoil2D.variables['mp'][:,:,:] = idSoil2D.variables['mp'][:,:,:]*float(newParams.mp[0])
        
        if param == "hvt":
            idSoil2D.variables['hvt'][:,:,:] = idSoil2D.variables['hvt'][:,:,:]*float(newParams.hvt[0])
        
        if param == "mfsno":
            idSoil2D.variables['mfsno'][:,:,:] = idSoil2D.variables['mfsno'][:,:,:]*float(newParams.mfsno[0])
        
        if param == "refkdt":
            idSoil2D.variables['refkdt'][:,:,:] = float(newParams.refkdt[0])
        
        if param == "dksat":
            idSoil2D.variables['dksat'][:,:,:,:] = idSoil2D.variables['dksat'][:,:,:,:]*float(newParams.dksat[0])
        
        if param == "retdeprtfac":
            idFullDom.variables['RETDEPRTFAC'][:,:] = float(newParams.retdeprtfac[0])
        
        if param == "ovroughrtfac":
            idFullDom.variables['OVROUGHRTFAC'][:,:] = float(newParams.ovroughrtfac[0])
            
        if param == "dksat":
            idHydroTbl.variables['LKSAT'][:,:] = idHydroTbl.variables['LKSAT'][:,:]*float(newParams.dksat[0])
            
        if param == "smcmax":
            idHydroTbl.variables['SMCMAX1'][:,:] = idHydroTbl.variables['SMCMAX1'][:,:]*float(newParams.smcmax[0])
            
        if param == "rsurfexp":
            idSoil2D.variables['rsurfexp'][:,:,:] = float(newParams.rsurfexp[0])
        
            
    # Close NetCDF files
    idFullDom.close()
    idSoil2D.close()
    idGw.close()
    idHydroTbl.close()
    
    # Remove restart files. All other files will be overwritten by the next
    # model iteration. 
    cmd = 'rm -rf ' + runDir + '/*.err'
    try:
        subprocess.call(cmd,shell=True)
    except:
        sys.exit(1)
    cmd = 'rm -rf ' + runDir + '/*.out'
    try:
        subprocess.call(cmd,shell=True)
    except:
        sys.exit(1)
    cmd = 'rm -rf ' + runDir + '/HYDRO_RST.*'
    try:
        subprocess.call(cmd,shell=True)
    except:
        sys.exit(4)
    cmd = 'rm -rf ' + runDir + '/RESTART.*'
    try:
        subprocess.call(cmd,shell=True)
    except:
        sys.exit(5)

    # Touch empty COMPLETE flag file. This will be seen by workflow, demonstrating
    # calibration iteration is complete.
    try:
        open(outFlag,'a').close()
    except:
        sys.exit(6)
            
if __name__ == "__main__":
    main(sys.argv[1:])