__version__ = '0.0.1'

__author__ = 'Jozef Svec'
__maintainer__ = 'Jozef Svec'
__email__ = 'jonyii@gmail.com'
__copyright__ = 'Copyright (c) 2017 jonyii'
__credits__ = ['Jozef Svec', 'Kyle Krafka']

from gacoxc.garminConnect import garminConnect, cachingGarminConnect
from gacoxc.simpleIGC import simpleIGC, gpx2igc

__all__= ['garminConnect', 'cachingGarminConnect', 'simpleIGC', 'gpx2igc']
