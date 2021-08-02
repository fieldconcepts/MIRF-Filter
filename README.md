# MIRF-Filter

Script that check for a existence of a new seismic file on a NAS drive. If new file exists the upsampled using a SciPy interpolation from 375us interval to 250us interval.

Common mode noise filter is applied to remove surface vibration from channels on fibre.

File is then re-writen into MIRF format with updated header values for SI and transferred to clients server.

Libraries used: mirf, scipy, numpy, re, time, os
