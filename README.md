# GArmin COnnect XC
Python library and scripts that can:
- download/cache Garmin Connect activities and records (gpx,..)
- convert GPX to IGC 
- upload relevant ones to Leonardo (global flight database)

# Install
pip install git+https://github.com/jonyii/gacoxc

# gaco
tool to download and cache garmin activities and records (backup purposes)  

example: gaco -u gcuser -d gpx kml --gpx2igc

usage: gaco [-h] [-v] [-u USERNAME] [-p PASSWORD] [-C CONFIG] [-D CACHE_DIR]  
            [-d [DOWNLOAD [DOWNLOAD ...]]] [--gpx2igc] [-n | -i]  
  
optional arguments:  
  -h, --help            show this help message and exit  
  -v, --verbose         verbose (more -vv)  
  -u USERNAME, --username USERNAME  
                        Garmin Connect username, you will be prompted  
                        otherwise  
  -p PASSWORD, --password PASSWORD  
                        Garmin Connect password, you will be prompted  
                        otherwise  
  -C CONFIG, --config CONFIG  
                        config file (define any cmdline line argument as k=v  
                        per line)  
  -D CACHE_DIR, --cache-dir CACHE_DIR  
                        garmin connect cache dir (default:  
                        ~/.garmin_connect_cache)  
  -d [DOWNLOAD [DOWNLOAD ...]], --download [DOWNLOAD [DOWNLOAD ...]]  
                        records to automatically download, supported: gpx tcx  
                        kml csv orig  
  --gpx2igc             auto convert gpx to igc, automatically downloads gpx  
  -n, --no-update       do not update latest activities, just download missing  
                        records of already cached activities  
  -i, --no-cache        ignore activity cache, re-download all activities  
  
gacoxc - tool to download gc recordings / upload to leonardo

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
