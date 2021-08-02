# MIRF-Filter

Script that periodically checks for a new seismic file on a NAS drive. If new file exists then it is read into memory and upsampled using a SciPy interpolation "signal.resample" from 375us interval to 250us interval.

Common mode noise filter is applied to remove surface vibration from channels on fibre.

File is then re-writen into MIRF format with updated header values for SI and transferred to clients server.

Libraries used: mirf, scipy, numpy, re, time, os
