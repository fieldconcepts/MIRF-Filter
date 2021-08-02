import mirf
import time
from scipy import signal
import numpy as np
import re
import os.path

### SCRIPT VARIABLES #########################################################

# Desired sample rate
fs = 4000

# The folder that the processed data will be saved to
upscaled_foldername = 'upscaled'

# Location of the data folder (can be absolute or relative to the script's path)
#source_location = 'data'
source_location = r"V:\210513 - 084811"

# Set the measured depth of the tool (metres)
measured_depth = 103.8

###############################################################################



workdir = os.path.abspath(source_location)


#target = workdir + os.path.sep + upscaled_foldername
#target = r"C:\data"
target =  r"G:\MPSStimulation2021\Avalon\BOSS\21_05_13B"

print("Current directory: {}".format(workdir))
print("Saving files to: {}".format(target))

### Create the target directory ###############################################

if not os.path.isdir(target):
    print("Creating target directory...",end='')
    os.mkdir(target)
    print("DONE")

### Get the highest record number in the folder ###############################

# Pattern for retrieving rcd number from the filename
file_pattern = re.compile("m_([0-9]{6})\.rcd")

# Declare initial rcd number
rcd = 0
#rcd = 797
for file in os.listdir(target):
    try:
        i = int(file_pattern.match(file).groups()[0])
        rcd = i if i > rcd else rcd # Essentially = max(i)
    except Exception:
        pass
    
# So the next file to process is...
rcd += 1
print("Will process from: m_{:06d}.rcd".format(rcd))

### Process the files #########################################################

need_sleep = False

while True:
    try:
        # Force sleep here (to prevent it being done whilst handling a FileNotFound error)
        if need_sleep:
            need_sleep = False
            time.sleep(6)
        
        f = mirf.MirfFile(workdir + os.path.sep + 'm_{:06d}.rcd'.format(rcd))

        data = f.get_all_data()[:,:] # Retrieve the data and drop the overlapping sample
        
        # Number of samples in a channel
        N0 = data.shape[0]
        
        seconds = round(N0/3125) # Get the number of seconds in the record
        N = seconds*fs # Calculate the number of samples we want (should be 24000 for 4kHz)
        
        upscaled = np.vstack((signal.resample(data[:-1,:],N,axis=0),data[-1,:])).astype('float32')

        N += 1
        
        ### Write upscaled data to a new MIRF file ####################################
        
        f.tool_depth = int(measured_depth *1000)
        
        for idx,ch in enumerate(f.channels):
            ch.data = upscaled[:,idx]
            ch.N = N
            ch.depth_offset *= 1000 # We will save this as (mm) as per MIRF spec
            ch.vertical_depth  = f.tool_depth + ch.depth_offset # Set TVD just in case
        
        # drop channel 10
        f.channel_count = 9
        f.channels = f.channels[:-1]
        print(len(f.channels))
        
        f.sample_period = int(1e6/fs)


        ### Start: remove common mode noise ##########################

        d = f.get_all_data()
        data = d.T

        # add all the channels together
        stack = data[0] 
        for i in range(1,data.shape[0]):
            stack = np.add(stack,data[i])
            
        ch_average = stack/data.shape[0] #take an aveage
        ch_average_i = ch_average * -1 # take inverse

        for i in range(len(f.channels)):
            denoised_ch = np.add(f.channels[i].data, ch_average_i)
            print(denoised_ch)
            f.channels[i].data = denoised_ch

        #### End: remove common mode noise ###############################



        print("Saving file: {}".format(target + os.path.sep + "m_{:06d}.rcd".format(rcd)))
        f.save_file(target + os.path.sep + "m_{:06d}.rcd".format(rcd))
        
        rcd += 1
    except FileNotFoundError:
        need_sleep = True # Don't sleep here (we can't accept keyboard interrupt while dealing with an error)
        print("File not found waiting 6 seconds!")
        continue
    
    except PermissionError:
        need_sleep = True # Don't sleep here (we can't accept keyboard interrupt while dealing with an error)
        print("Permission Error - waiting 6 seconds!")
        continue

    except KeyboardInterrupt:
        break
    
    
    
print("Upsampling script has terminated")