import gpxpy

class simpleIGC(object):

    latlong_map= {True: { True: 'S', False: 'N'},
                 False: { True: 'W', False: 'E'}}
    
    def __init__(self, date, pilot_name, glider_type=None):
        self.data = []

        self.add("A","XXX","ZZZ","simpleIGC by jonyii")
        self.add("H","F","DTE", date)
        self.add("H","F","PLT","PILOTINCHARGE:", pilot_name)
        if glider_type:
            self.add("H","F","GTY","GLIDERTYPE:", glider_type)

    def add(self, *args):
        self.data.append(''.join([str(x) for x in args]))

    def _decimal2DMS(self, ll, is_lat=True):
        dec = abs(ll)
        return '%0.*d%05d%s' % (
                                2 if is_lat else 3,
                                int(dec),  # DD/DDD degrees lat/long
                                round((dec % 1) * 60000), # MMmmm minutes and decimal minutes
                                self.latlong_map.get(is_lat).get(ll < 0) # map S/N or W/E depending on lat/long
                              )

    def add_B(self, time, dec_lat, dec_lng, press_alt, gps_alt):
        self.add("B", 
                 time.strftime('%H%M%S'),
                 self._decimal2DMS(dec_lat, True),
                 self._decimal2DMS(dec_lng, False),
                 'A' if (press_alt or gps_alt) else 'V',
                 '%05d' % (press_alt or 0),
                 '%05d' % (gps_alt or 0)
                )

    def __str__(self):
        return self.get_igc()

    def get_igc(self):
        return '\r\n'.join(self.data) + '\r\nGsimpleIGCSecurityRecordGuaranteedToFailVALIChecks\r\n'
    
def gpx2igc(gpx, pilot_name, glider_type=None):
    "expecting GPX as bytes"
    g = gpxpy.parse(gpx.decode("utf-8"))

    if len(g.tracks) > 1:
        print("WARNING: %d tracks found, they will be merged into single track"%(len(gpx.tracks)))

    date = g.time.strftime('%d%m%y')
    igc = simpleIGC(date, pilot_name, glider_type)

    for track in g.tracks:
        for segment in track.segments:
            for point in segment.points:
                igc.add_B(point.time, point.latitude, point.longitude, None, point.elevation)

    return str(igc)

