from distutils.core import setup
import sys

import gacoxc


requires = ['gpxpy']
if sys.version_info < (2, 7):
    requires += ['argparse']

setup(
    name='gacoxc',
    version=gacoxc.__version__,
    description='GArmin COnnect XC: Python library and scripts to download/cache Garmin Connect activities and records (gpx,..), convert GPX to IGC and upload relevant ones to Leonardo (global flight database)',
    author='Jozef Svec',
    author_email='jonyii@gmail.com',
    url='https://github.com/jonyii/gacoxc',
    license=open('LICENSE').read(),
    packages=['gacoxc'],
    scripts=['scripts/gaco'],
    install_requires=requires,
)
