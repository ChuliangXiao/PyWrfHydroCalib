# This is a utiltiy program for the user to do a quick dump of where
# their calibration job is at for each basin. The user has the option
# to either print to the screen, or send the output to the job 
# contact information. 

# Logan Karsten
# National Center for Atmospheric Research
# Research Applications Laboratory
# 303-497-2693
# karsten@ucar.edu

import argparse
#import pwd
import sys
import os

# Set the Python path to include package specific functions.
prPath = os.path.realpath(__file__)
pathSplit = prPath.split('/')
libPath = '/'
for j in range(1,len(pathSplit)-2):
    libPath = libPath + pathSplit[j] + '/'
libPath = libPath + 'lib/Python'
sys.path.insert(0,libPath)

import statusMod
import dbMod
import errMod

def main(argv):
    # Parse arguments. User must input a job name and directory.
    parser = argparse.ArgumentParser(description='Utility program to report the position' + \
                                     ' of a calibration job.')
    parser.add_argument('jobID',metavar='jobID',type=str,nargs='+',
                        help='Job ID specific to calibration spinup.')
    parser.add_argument('contactFlag',metavar='ctFlag',type=int,nargs='+',
                        help='1 = send to job contact, 0 = print to screen.')
    parser.add_argument('--email',nargs='?',help='Optional email to pipe output to.')
                        
    args = parser.parse_args()
    
    # Create dictionary of specified status messages.
    msgDict = {'-1.0':'MODEL RUN LOCKED.','-0.75':'MAIN CALIBRATION PROGRAM LOCKED',
               '-0.5':'MODEL FAILED ONCE - RUNNING AGAIN','-0.25':'MODEL FAILED ONCE - WAITING',
               '-0.1':'CALIBRATON PROGRAM FOR DEFAULT PARAMETERS LOCKED',
               '0.0':'NOT STARTED','0.25':'CALIBRATION PROGRAM FOR DEFAULT PROGRAM RUNNING',
               '0.5':'MODEL CURRENTLY RUNNING','0.75':'MODEL COMPLETE READY FOR PARAMETER ESTIMATION',
               '0.9':'PARAMETER ESTIMATION OCCURRING'}
    
    # Initialize object to hold status and job information
    jobData = statusMod.statusMeta()
    jobData.jobID = int(args.jobID[0])

    # Lookup database username/login credentials based on username
    # running program.
    #try:
    #    uNameTmp = raw_input('Enter Database Username: ')
    #    pwdTmp = getpass.getpass('Enter Database Password: ')
    #    jobData.dbUName= str(uNameTmp)
    #    jobData.dbPwd = str(pwdTmp)
    #except:
    #    print "ERROR: Unable to authenticate credentials for database."
    #    sys.exit(1)
    
    jobData.dbUName = 'NWM_Calib'
    jobData.dbPwd = 'CalibrateGoodTimes'
    
    # Establish database connection.
    db = dbMod.Database(jobData)
    try:
        db.connect(jobData)
    except:
        print jobData.errMsg
        sys.exit(1)
        
    # Extract job data from database
    try:
        db.jobStatus(jobData)
    except:
        print jobData.errMsg
        sys.exit(1)
        
    # Check gages in directory to match what's in the database
    try:
        jobData.checkGages(db)
    except:
        errMod.errOut(jobData)
        
    # If an optional email was passed to the program, update the job object to 
    # reflect this for information dissemination.
    print "OLD EMAIL: " + str(jobData.email)
    if args.email:
        jobData.slackObj = None
        jobData.email = str(args.email)

    print "NEW EMAIL: " + str(jobData.email)        
    # Loop through each basin. Determine if which iteration we are on, then report the status
    # of the job for this basin.
    msgOut = ''
    for basin in range(0,len(jobData.gages)):
        keyStatus = 0.0
        keyStatusPrev = 0.0
        # First pull the unique ID for the basin. 
        try:
            domainID = db.getDomainID(jobData,str(jobData.gages[basin]))
        except:
            errMod.errOut(jobData)
        iterComplete = 1 
        for iteration in range(0,int(jobData.nIter)):
            keyStatus = db.iterationStatus(jobData,domainID,iteration,str(jobData.gages[basin]))
            if keyStatus == 1.0:
                if iterComplete == int(jobData.nIter):
                    msgOut = msgOut + "BASIN: " + str(jobData.gages[basin]) + \
                             ": CALIBRATION COMPLETE.\n"
                else:
                    iterComplete = iterComplete + 1
            elif keyStatus == 0.0 and keyStatusPrev == 1.0:
                msgOut = msgOut + "BASIN: " + str(jobData.gages[basin]) + \
                         " - IS READY TO BEGIN ITERATION: " + str(iteration+1) + "\n " 
            else:
                #print '------------------'
                #print keyStatusPrev
                #print iteration
                #print keyStatus
                if keyStatusPrev == 0.0 and iteration == 0 and keyStatus == 0.0:
                    msgOut = msgOut + "BASIN: " + str(jobData.gages[basin]) + \
                             " - HAS NOT BEGUN CALIBRATION.\n"
                if keyStatusPrev == 1.0 and iteration != 0:
                    msgOut = msgOut + "BASIN: " + str(jobData.gages[basin]) + \
                             ": " + str(msgDict[str(keyStatus)]) + \
                             " - ITERATION: " + str(iteration+1) + "\n"
                if keyStatusPrev == 0.0 and iteration == 0 and keyStatus != 0.0:
                    msgOut = msgOut + "BASIN: " + str(jobData.gages[basin]) + \
                             ": " + str(msgDict[str(keyStatus)]) + \
                             " - ITERATION: " + str(iteration+1) + "\n"
            keyStatusPrev = keyStatus
                         
    jobData.genMsg = msgOut
    print "FLAG = " + str(args.contactFlag)
    if int(args.contactFlag[0]) == 0:
        print "LKJALGKFJAKLFJ"
        print jobData.genMsg
    else:
        errMod.sendMsg(jobData)
                
                
if __name__ == "__main__":
    main(sys.argv[1:])