# GArmin COnnect XC
Python library and scripts that can:
- download/cache Garmin Connect activities and records (gpx,..)
- convert GPX to IGC 
- upload relevant ones to Leonardo (global flight database)

# Install
pip install git+https://github.com/jonyii/gacoxc

# Use
gaco - tool to download and cache garmin activities and records (backup purposes)
gacoxc - tool to 

# Config files
tools support simple config file that contains key=value pairs, where you can define any commandline parameter.
If the key does not match any of cmdline options, it's ignored.

example for gaco:
username = your-gc-username
password = your-gc-password
#verbose=2
download = gpx orig
gpx2igc = True

# License
This project is licensed under the MIT License - see the [`LICENSE`](LICENSE)
file for details.
