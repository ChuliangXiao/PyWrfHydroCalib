# Main calling program to initiate a validation of the National
# Water Model. This program is built on the premise that spinup
# and full calibration of the basin has occurred to completion. 
# This portion of the workflow will run the model in a similar 
# fashion as with the spinup. Once the simulation is complete,
# an R program is executed to generate statistics and plots.

# Logan Karsten
# National Center for Atmospheric Research
# Research Applications Laboratory
# karsten@ucar.edu
# 303-497-2693

import sys
import argparse
#import getpass
import os
#import subprocess
#import pandas as pd
import pwd
import numpy as np

# Set the Python path to include package specific functions.
prPath = os.path.realpath(__file__)
pathSplit = prPath.split('/')
libPath = '/'
for j in range(1,len(pathSplit)-1):
    libPath = libPath + pathSplit[j] + '/'
libPath = libPath + 'lib/Python'
sys.path.insert(0,libPath)

import warnings
warnings.filterwarnings("ignore")

import statusMod
import dbMod
import errMod
import validMod
import configMod
import time

def main(argv):
    # Parse arguments. User must input a job name.
    parser = argparse.ArgumentParser(description='Main program to start or restart the ' + \
             'calibration validation simulation for the National Water Model')
    parser.add_argument('jobID',metavar='jobID',type=str,nargs='+',
                        help='Job ID specific to calibration validation.')
    
    args = parser.parse_args()
    
    # Get current user who is running this program.
    userTmp = pwd.getpwuid(os.getuid()).pw_name
    
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
    
    jobData.dbUName = 'NWM_Calib_rw'
    jobData.dbPwd = 'IJustWannaCalibrate'    
    
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
    
    # Pull extensive meta-data describing the job from the config file.
    configPath = str(jobData.jobDir) + "/setup.config"
    if not os.path.isfile(configPath):
        print "ERROR: Configuration file: " + configPath + " not found."
        sys.exit(1)

    try:        
        staticData = configMod.readConfig(configPath)
    except:
        print "ERROR: Failure to read configuration file: " + configPath
        sys.exit(1)
        
    # Check gages in directory to match what's in the database
    try:
        jobData.checkGages(db)
    except:
        errMod.errOut(jobData)
    
    # Extract active jobs for job owner
    try:
        statusMod.checkYsJobs(jobData)
    except:
        errMod.errOut(jobData)
    
    # Some house keeping here. If the validation is already complete, throw an error. 
    # also, if this is a re-initiation under a different user, require the new
    # user to enter a new contact that will be unpdated in the database. 
    # Also require that both the spinup and calibrations have been entered into
    # the database as complete. 
    if int(jobData.validComplete) == 1:
        jobData.errMsg = "ERROR: Validation for job ID: " + str(jobData.jobID) + \
                         " has already completed."
        errMod.errOut(jobData)
    if int(jobData.spinComplete) != 1:
        jobData.errMsg = "ERROR: Spinup for job ID: " + str(jobData.jobID) + \
                         " has NOT completed. Please complete spinup before " + \
                         " proceeding."
        errMod.errOut(jobData)
    if int(jobData.calibComplete) != 1:
        jobData.errMsg = "ERROR: Calibration for job ID: " + str(jobData.jobID) + \
                         " has NOT completed. Please complete calibration before " + \
                         " proceeding."
        errMod.errOut(jobData)
        
    if userTmp != jobData.owner:
        #print "User: " + userTmp + " is requesting to takeover jobID: " + \
        #      str(jobData.jobID) + " from owner: " + str(jobData.owner)
        #strTmp = "Please enter new email address. Leave blank if no email " + \
        #         "change is desired. NOTE if you leave both email and Slack " + \
        #         "information blank, no change in contact will occur. Only " + \
        #         "the owner will be modified:"
        #newEmail = raw_input(strTmp)
        #strTmp = "Please enter Slack channel:"
        #newSlackChannel = raw_input(strTmp)
        #strTmp = "Please enter Slack token:"
        #newSlackToken = raw_input(strTmp)
        #strTmp = "Please enter Slack user name:"
        #newSlackUName = raw_input(strTmp)
        changeFlag = 1
        #if len(newSlackChannel) != 0 and len(newSlackToken) == 0:
        #    print "ERROR: You must specify an associated Slacker API token."
        #    sys.exit(1)
        #if len(newSlackChannel) != 0 and len(newSlackUName) == 0:
        #    print "ERROR: You must specify an associated Slacker user name."
        #    sys.exit(1)
        #if len(newSlackToken) != 0 and len(newSlackChannel) == 0:
        #    print "ERROR: You must specify an associated Slacker channel name."
        #    sys.exit(1)
        #if len(newSlackToken) != 0 and len(newSlackUName) == 0:
        #    print "ERROR: You must specify an associated Slacker user name."
        #    sys.exit(1)
        #if len(newSlackUName) != 0 and len(newSlackChannel) == 0:
        #    print "ERROR: You must specify an associated Slacker channel name."
        #    sys.exit(1)
        #if len(newSlackUName) != 0 and len(newSlackToken) == 0:
        #    print "ERROR: You must specify an associated Slacker API token."
        #    sys.exit(1)
        #if len(newSlackChannel) != 0 and len(newEmail) != 0:
        #    print "ERROR: You cannot specify both email and Slack for notifications."
        #    sys.exit(1)
        #if len(newSlackChannel) == 0 and len(newEmail) == 0:
        #    changeFlag = 0
            
        # PLACEHOLDER FOR CHECKING SLACK CREDENTIALS
            
        # TEMPORARY FOR VERSION 1.2 NWM CALIBRATION!!!!
        # If a new owner takes over, simply change the owner, but keep all 
        # other contact information the same.
        newEmail = jobData.email
        newSlackChannel = jobData.slChan
        newSlackToken = jobData.slToken
        newSlackUName = jobData.slUser
        if not newEmail:
            newEmail = ''
        if not newSlackChannel:
            newSlackChannel = ''
            newSlackToken = ''
            newSlackUName = ''
            
        try:
            db.updateJobOwner(jobData,userTmp,newEmail,newSlackChannel,newSlackToken,newSlackUName,changeFlag)
        except:
            errMod.errOut(jobData)
            
        jobData.genMsg = "MSG: User: " + userTmp + " Is Taking Over JobID: " + str(jobData.jobID) + \
                         " From Owner: " + str(jobData.owner)
        errMod.sendMsg(jobData)
            
    # Begin an "infinite" do loop. This loop will continue to loop through all 
    # the basins until spinups are complete. Basins are allowed ONE failure. A restart
    # will be attempted. If the restart fails again, a LOCK file is placed into the
    # run directory and an error email is sent to the user.
    completeStatus = False
    
    # Create a "key" array. This array is of length [numBasins] and is initialized to 0.0.
    # Each array element can have the following values based on current model status:
    # 0.0 - Initial value
    # 0.5 - Model simulation in progress
    # 1.0 - Model simulation complete
    # -0.5 - Model simulation failed once and a restart has been attempted
    # -1.0 - Model has failed twice. A LOCK file has been created.
    # Once all array elements are 1.0, then completeStatus goes to True, an entry into
    # the database occurs, and the program will complete.
    keySlot = np.empty(len(jobData.gages),2)
    keySlot[:] = 0.0
    entryValue = float(len(jobData.gages))*2.0
    
    while not completeStatus:
        # Walk through spinup directory for each basin. Determine the status of
        # the model runs by the files available. If restarting, modify the 
        # namelist files appropriately. Then, restart the model. Once all
        # basins have been accounted for, fire off the monitoring program through
        # nohup to keep track of the models. If anything goes wrong, notifications
        # will either be emailed per the user's info, or piped to Slack for group
        # notification.
        # Loop through each basin. Perform the following steps:
        # 1.) If status is -0.5,0.0, or 0.5, check to see if the model is running
        #     for this basin.
        # 2.) If the model is not running, check for expected output and perform
        #     necessary logistics. Continue to the next basin.
        # If the status goes to -1.0, a LOCK file is created and must be manually
        # removed from the user. Once the program detects this, it will restart the
        # model and the status goes back to 0.5.
        # If the status is -0.5 and no job is running, output must be complete, or 
        # status goes to -1.0.
        # If output is not complete, the model is still running, status stays at 0.5.
        # If job is not running, and output has been completed, status goes to 1.0.
        # This continues indefinitely until statuses for ALL basins go to 1.0.
        for basin in range(0,len(jobData.gages)):
            for run in range(0,2):
                # First simulation will be the control simulation with default
                # parameters specified by the user at the beginning of the calibration
                # process.
                print keySlot
                try:
                    validMod.runModel(jobData,staticData,db,jobData.gageIDs[basin],jobData.gages[basin],keySlot,basin,run)
                except:
                    errMod.errOut(jobData)
                time.sleep(30)
        
        # Check to see if program requirements have been met.
        if keySlot.sum() == entryValue:
            jobData.spinComplete = 1
            try:
                db.updateSpinupStatus(jobData)
            except:
                errMod.errout(jobData)
            jobData.genMsg = "SPINUP FOR JOB ID: " + str(jobData.jobID) + " COMPLETE."
            errMod.sendMsg(jobData)
            completeStatus = True
    
if __name__ == "__main__":
    main(sys.argv[1:])