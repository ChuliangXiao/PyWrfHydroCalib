# Python program to generate the set of parameter files for validation.
# The parameter values are taken from the database (from workflow), and 
# read in via a table. These values are then applied to basline parameter
# values stored in the RUN.CALIB directory. Symbolic links are made to the 
# default parameter directory for the control run. 

# Logan Karsten
# National Center for Atmospheric Research
# Researc Applications Laboratory
# karsten@ucar.edu
# 303-497-2693

import argparse
import sys
from netCDF4 import Dataset
import os
import shutil
import pandas as pd
import numpy as np

def main(argv):
    # Parse arguments. Only input necessary is the run directory.
    parser = argparse.ArgumentParser(description='Main program to adjust input ' + \
             'parameters for the validation run of the National Water Model')
    parser.add_argument('bestDir',metavar='bestDir',type=str,nargs='+',
                        help='Directory where best parameters for model run will reside.')
    parser.add_argument('paramDir',metavar='paramDir',type=str,nargs='+',
                        help='Directory containing the baseline parameter files to be adjusted.')
    parser.add_argument('ctrlDir',metavar='ctrlDir',type=str,nargs='+',
                        help='Directory where the control default model simulation will take place')
    parser.add_argument('defDir',metavar='defDir',type=str,nargs='+',
                        help='Directory where the default parameter files from the calibration exist.')
                        
    args = parser.parse_args()
    bestDir = str(args.bestDir[0])
    paramDir = str(args.paramDir[0])
    ctrlDir = str(args.ctrlDir[0])
    defDir = str(args.defDir[0])
    
    # Compose input file paths.
    fullDomOrig = paramDir + "/Fulldom.nc"
    hydroOrig = paramDir + "/HYDRO_TBL_2D.nc"
    soilOrig = paramDir + "/soil_properties.nc"
    gwOrig = paramDir + "/GWBUCKPARM.nc"
    
    fullDomDefault = defDir + "/Fulldom.nc"
    hydroDefault = defDir + "/HYDRO_TBL_2D.nc"
    soilDefault = defDir + "/soil_properties.nc"
    gwDefault = defDir + "/GWBUCKPARM.nc"

    fullDomBest = bestDir + "/Fulldom.nc"
    hydroBest = bestDir + "/HYDRO_TBL_2D.nc"
    soilBest = bestDir + "/soil_properties.nc"
    gwBest = bestDir + "/GWBUCKPARM.nc"
    
    # First make symbolic links in the control run directory to the default files.
    link = ctrlDir + "/Fulldom.nc"
    if not os.path.islink(link):
        os.symlink(fullDomDefault,link)
    link = ctrlDir + "/HYDRO_TBL_2D.nc"
    if not os.path.islink(link):
        os.symlink(hydroDefault,link)
    link = ctrlDir + "/soil_properties.nc"
    if not os.path.islink(link):
        os.symlink(soilDefault,link)
    link = ctrlDir + "/GWBUCKPARM.nc"
    if not os.path.islink(link):
        os.symlink(gwDefault,link)
    
    # Next, open up table file generated by the workflow.
    dbTable = bestDir + "/parms_best.tbl"
    
    if not os.path.isfile(dbTable):
        sys.exit(1)
        
    # Copy baseline parameter values to best directory for adjustment
    try:
        shutil.copy(fullDomOrig,fullDomBest)
        shutil.copy(soilOrig,soilBest)
        shutil.copy(gwOrig,gwBest)
        shutil.copy(hydroOrig,hydroBest)
    except:
        sys.exit(3)
        
    # Read in new parameters table.
    newParams = pd.read_csv(dbTable,sep=',')
    paramNames = newParams.paramName.values
    paramValues = newParams.paramValue.values

    # Open NetCDF parameter files for adjustment.
    idFullDom = Dataset(fullDomBest,'a')
    idSoil2D = Dataset(soilBest,'a')
    idGw = Dataset(gwBest,'a')
    idHydroTbl = Dataset(hydroBest,'a')
    
    # Loop through and adjust each parameter accordingly.
    for param in paramNames:
        print param
        if param == "bexp":
            idSoil2D.variables['bexp'][:,:,:,:] = idSoil2D.variables['bexp'][:,:,:,:]*float(paramValues[np.where(paramNames == 'bexp')[0][0]])
        
        if param == "smcmax":
            idSoil2D.variables['smcmax'][:,:,:,:] = idSoil2D.variables['smcmax'][:,:,:,:]*float(paramValues[np.where(paramNames == 'smcmax')[0][0]])
        
        if param == "slope":
            idSoil2D.variables['slope'][:,:,:] = float(paramValues[np.where(paramNames == 'slope')[0][0]])
        
        if param == "lksatfac":
            idFullDom.variables['LKSATFAC'][:,:] = float(paramValues[np.where(paramNames == 'lksatfac')[0][0]])
        
        if param == "zmax":
            idGw.variables['Zmax'][:] = float(paramValues[np.where(paramNames == 'zmax')[0][0]])
        
        if param == "expon":
            idGw.variables['Expon'][:] = float(paramValues[np.where(paramNames == 'expon')[0][0]])
        
        if param == "cwpvt":
            idSoil2D.variables['cwpvt'][:,:,:] = idSoil2D.variables['cwpvt'][:,:,:]*float(paramValues[np.where(paramNames == 'cwpvt')[0][0]])
        
        if param == "vcmx25":
            idSoil2D.variables['vcmx25'][:,:,:] = idSoil2D.variables['vcmx25'][:,:,:]*float(paramValues[np.where(paramNames == 'vcmx25')[0][0]])
        
        if param == "mp":
            idSoil2D.variables['mp'][:,:,:] = idSoil2D.variables['mp'][:,:,:]*float(paramValues[np.where(paramNames == 'mp')[0][0]])
        
        if param == "hvt":
            idSoil2D.variables['hvt'][:,:,:] = idSoil2D.variables['hvt'][:,:,:]*float(paramValues[np.where(paramNames == 'hvt')[0][0]])
        
        if param == "mfsno":
            idSoil2D.variables['mfsno'][:,:,:] = idSoil2D.variables['mfsno'][:,:,:]*float(paramValues[np.where(paramNames == 'mfsno')[0][0]])
        
        if param == "refkdt":
            idSoil2D.variables['refkdt'][:,:,:] = float(paramValues[np.where(paramNames == 'refkdt')[0][0]])
        
        if param == "dksat":
            idSoil2D.variables['dksat'][:,:,:,:] = idSoil2D.variables['dksat'][:,:,:,:]*float(paramValues[np.where(paramNames == 'dksat')[0][0]])
        
        if param == "retdeprtfac":
            idFullDom.variables['RETDEPRTFAC'][:,:] = float(paramValues[np.where(paramNames == 'retdeprtfac')[0][0]])
        
        if param == "ovroughrtfac":
            idFullDom.variables['OVROUGHRTFAC'][:,:] = float(paramValues[np.where(paramNames == 'ovroughrtfac')[0][0]])
        
        if param == "dksat":
            idHydroTbl.variables['LKSAT'][:,:] = idHydroTbl.variables['LKSAT'][:,:]*float(paramValues[np.where(paramNames == 'dksat')[0][0]])
            
        if param == "smcmax":
            idHydroTbl.variables['SMCMAX1'][:,:] = idHydroTbl.variables['SMCMAX1'][:,:]*float(paramValues[np.where(paramNames == 'smcmax')[0][0]])
            
        if param == "rsurfexp":
            idSoil2D.variables['rsurfexp'][:,:,:] = float(paramValues[np.where(paramNames == 'rsurfexp')[0][0]])
            
    # Close NetCDF files
    idFullDom.close()
    idSoil2D.close()
    idGw.close()
    idHydroTbl.close()

    # Touch empty COMPLETE flag file. This will be seen by workflow, demonstrating
    # calibration iteration is complete.
    outFlag = bestDir + "/PARAM_GEN.COMPLETE"
    try:
        open(outFlag,'a').close()
    except:
        sys.exit(6)
        
if __name__ == "__main__":
    main(sys.argv[1:])