#!/usr/bin/python

"""
GarminConnect library including wapper cachingGarminConnect

Author: Jozef Svec https://github.com/jonyii
Based on: gcexport.py by Kyle Krafka (https://github.com/kjkjava/)
"""

from urllib.parse import urlencode
import urllib.request, urllib.error, urllib.parse, http.cookiejar
import json
from collections import OrderedDict

class garminConnect(object):

    # Maximum number of activities you can request at once.  Set and enforced by Garmin.
    gc_max_req_limit = 100
    # URLs for various services.
    gc_url_login     = 'https://sso.garmin.com/sso/login?service=https%3A%2F%2Fconnect.garmin.com%2Fpost-auth%2Flogin&webhost=olaxpw-connect04&source=https%3A%2F%2Fconnect.garmin.com%2Fen-US%2Fsignin&redirectAfterAccountLoginUrl=https%3A%2F%2Fconnect.garmin.com%2Fpost-auth%2Flogin&redirectAfterAccountCreationUrl=https%3A%2F%2Fconnect.garmin.com%2Fpost-auth%2Flogin&gauthHost=https%3A%2F%2Fsso.garmin.com%2Fsso&locale=en_US&id=gauth-widget&cssUrl=https%3A%2F%2Fstatic.garmincdn.com%2Fcom.garmin.connect%2Fui%2Fcss%2Fgauth-custom-v1.1-min.css&clientId=GarminConnect&rememberMeShown=true&rememberMeChecked=false&createAccountShown=true&openCreateAccount=false&usernameShown=false&displayNameShown=false&consumeServiceTicket=false&initialFocus=true&embedWidget=false&generateExtraServiceTicket=false'
    gc_url_post_auth = 'https://connect.garmin.com/post-auth/login?'
    gc_url_logout    = 'https://connect.garmin.com/auth/logout'
    gc_url_search    = 'https://connect.garmin.com/proxy/activity-search-service-1.0/json/activities?'
    gc_url_gpx_activity = 'https://connect.garmin.com/proxy/download-service/export/gpx/activity/'
    gc_url_tcx_activity = 'https://connect.garmin.com/proxy/download-service/export/tcx/activity/'
    gc_url_kml_activity = 'https://connect.garmin.com/proxy/download-service/export/kml/activity/'
    gc_url_csv_activity = 'https://connect.garmin.com/proxy/download-service/export/csv/activity/'
    gc_url_original_activity = 'https://connect.garmin.com/proxy/download-service/files/activity/'
        
    gc_type_to_download_url = {
                                'gpx': gc_url_gpx_activity,
                                'tcx': gc_url_tcx_activity,
                                'kml': gc_url_kml_activity,
                                'csv': gc_url_csv_activity,
                                'orig': gc_url_original_activity,
                            }
    
    def __init__(self, username, password, verbose=0, login=True):
        self.cookie_jar = http.cookiejar.CookieJar()
        self.url_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        self.v = verbose

        self.username = username
        self.password = password

        self.sum = []
        self.activities = []    
        self.records = {}
        self.loggedin = False

        if login:
            self.login()

    def login(self):
        if self.v: print("Logging in...")
        # prep the sesion and login   
        self.loggedin = True
        try: 
            self._http_req(self.gc_url_login) # init cookies
            self._http_req(self.gc_url_login, {
                            'username': self.username, 
                            'password': self.password, 
                            'embed': 'true', 
                            'lt': 'e1s1', 
                            '_eventId': 'submit', 
                            'displayNameRequired': 'false'} )
            login_ticket = 'ST-0' + ([c.value for c in self.cookie_jar if c.name == 'CASTGC'][0])[4:]
        except:
            self.loggedin = False
            raise Exception('Did not get a ticket cookie. Cannot log in. Did you enter the correct username and password?')

        self._http_req(self.gc_url_post_auth + 'ticket=' + login_ticket)
        if self.v: print("Logged in!")
        self.loggedin = True

    def logout(self):
        if self.loggedin:
            if self.v: print("Logging out...")
            self._http_req(self.gc_url_logout)
            self.loggedin = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logout()

    def __iter__(self):
        for a in self.activities:
            yield a

    def __len__(self):
        return len(self.sum)

    def __getitem__(self, key):
        return self.activities[key]

    # url is a string, post is a dictionary of POST parameters, headers is a dictionary of headers.
    def _http_req(self, url, post=None, headers={}):
        if not self.loggedin:
            self.login()
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/1337 Safari/537.36')  # Tell Garmin we're some supported browser.
        for header_key, header_value in list(headers.items()):
            request.add_header(header_key, header_value)
        if post:
            post = urlencode(post).encode("utf-8")  # Convert dictionary to POST parameter string.
        if self.v > 1: print("requesting url %s with post data %s" %(url, post))
        response = self.url_opener.open(request, data=post)

        #if response.getcode() != 200:
        #    raise Exception('Bad return code (' + str(response.getcode()) + ') for: ' + url)

        return response.read()

    def download_activities(self, how_many=1, getAll=False, ignoreNonGPS=False, sortOrder='DESC', sortField='activitySummaryBeginTimestampGmt'):
        """
           if sortOrder='DESC': start downloading from the latest activity
        """
        self.activities = []

        downloaded = 0
        if getAll:
            how_many = self.gc_max_req_limit

        while downloaded < how_many:
            to_download = min(how_many-downloaded, self.gc_max_req_limit)

            result = self._http_req(self.gc_url_search + urlencode({
                                                'start': downloaded, 
                                                'limit': to_download,
                                                'ignoreNonGPS': ignoreNonGPS,
                                                'sortOrder': sortOrder,
                                                'sortField': sortField,
                                              })
                             )
            json_results = json.loads(result)  # TODO: Catch possible exceptions here.
        
            if getAll:
                how_many = int(json_results['results']['search']['totalFound'])
                getAll = False

            actv = json_results['results']['activities']
            self.activities.extend(actv)

            downloaded += len(actv)
            if len(actv) < to_download:
                if self.v>1: print("Got only %d activities, orig requested %d, total got %d / expected %d" %(len(actv), to_download, downloaded, how_many))
                break # we are done here

            if self.v>1: print("Downloaded %d / %d activities" %(downloaded, how_many))
        if self.v: print("Downloaded %d activities" %(len(self.activities)))

        self.sum = self._gen_summary()
        return self.activities

    def summary(self, firstn=None, as_string=True):
        "return first n activities"
        firstn = len(self.sum) if firstn is None else firstn
        if as_string:
            return "\n".join([str(i)+"\t"+"\t".join([v for k,v in list(a.items())]) for i,a in enumerate(self.sum[:firstn])])
        else:
            return self.sum[:firstn]
        
    def _gen_summary(self):
        def getfield(a, field, preferred='_'):
            if field in a:
                aa=a[field]
                for f in [preferred, 'display', 'value']:
                    if f in aa:
                        return aa[f]
            return 'n/a'
        summ = []
        for act in self.activities:
            a = act['activity']
            asum = OrderedDict([
                    ('id', a['activityId']),
                    ('start', getfield(a, 'beginTimestamp')),
                    ('duration', getfield(a, 'sumElapsedDuration')),
                    ('distance', getfield(a, 'sumDistance', 'withUnit')),
                    ('name', getfield(a, 'activityName')),
                  ])
            summ.append(asum)
        return summ 

    def get_cached_record(self, aid, fmt): 
        if fmt=='orig': fmt = 'zip'
        return self.records.get(aid,{}).get(fmt)

    def cache_record(self, aid, fmt, data):
        if data is None:
            data=''
        if aid not in self.records:
            self.records[aid] = {fmt: data}
        else:
            self.records[aid][fmt] = data

    def actid(self, activity):
        "get activity id from one of activity representations"
        if isinstance(activity, str):
            return activity
        elif isinstance(activity, int):
            return self.sum[activity]['id']
        elif 'id' in activity: # from summary
            return activity['id']
        elif 'activity' in activity: # from original activity
            return activity['activity']['activityId']
        else:
            raise Exception("No activity ID found in supplied activity")


    def download_record(self, act, fmt='orig'):
        "fmt could be gpx|tcx|kml|original|kml|csv|... whatever is supported or user cached"
        aid = self.actid(act)

        # check the cache
        data = self.get_cached_record(aid, fmt)
        if data is not None:
            return data
        if self.v: print("Downloading %s record for activity id %s" % (fmt, aid))

        # we allow to cache exotic stuff, hence check format only here
        downurl = self.gc_type_to_download_url.get(fmt, None)
        if downurl is None:
            raise Exception('Unrecognized format.')

        try:
            data = self._http_req(downurl + str(aid))
        except urllib.error.HTTPError as e:
            # Handle expected (though unfortunate) error codes; die on unexpected ones.
            if e.code == 204:
                print("ERROR: acitivity has no GPS data")
            elif e.code == 500 and fmt == 'tcx':
                print('ERROR: Garmin did not generate a TCX file for this activity...')
            elif e.code == 404:
                print('ERROR: Garmin did not provide activity data...')
            elif e.code == 410 and fmt == 'gpx':
                print('ERROR: Garmin did not provide gpx file...')
            elif float(activity['activity'].get('sumDistance',{}).get('value',0.0)) == 0.0:
                print('ERROR: This activity has zero distance in descritption, probably does not have records do download...')
            else:
                raise Exception('Failed. Got an unexpected HTTP error (' + str(e.code) + ').')
            data = None

        self.cache_record(aid, fmt, data)

        return data

import os
import csv
import json
#import pprint

class cachingGarminConnect(garminConnect):

    gc_sum_file='summary.csv'

    def __init__(self, username, password, verbose=0, cache_dir='~/.garmin_connect_cache', update=False):
        self.cache_dir = os.path.expanduser(cache_dir)

        if not os.path.isdir(self.cache_dir):
            if verbose: print("Creating cache directory ", self.cache_dir)
            os.mkdir(self.cache_dir)

        super(cachingGarminConnect, self).__init__(username, password, verbose, login=update)

        self.sum_file = os.path.join(self.cache_dir, self.gc_sum_file)
        self._load_sum()
        if update:
            self.update()

    def _load_sum(self):
        self.sum = []
        if os.path.isfile(self.sum_file):
            if self.v: print("Loading cached acitivy summary from ", self.sum_file)
            with open(self.sum_file) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.sum.append(row)
        
    def _load_activity(self, aid, fmt='json'):
        if fmt=='orig': fmt = 'zip'
        adir = os.path.join(self.cache_dir, aid)
        if not os.path.isdir(adir):
            print("ERROR: activity",aid,'is not cached on disk, likely screwed cache (workaround: ignore cache)')
            # TODO download the activity - files were deleted?
            return

        ajsonf = os.path.join(adir, aid+'.'+fmt)
        if os.path.isfile(ajsonf):
            if self.v: print(" >> loading cached "+aid+"."+fmt)
            openlike = 'r' if fmt in ['json','igc'] else 'rb'
            with open(ajsonf, openlike) as f:
                if fmt=='json':
                    self.activities.append(json.loads(f.read()))
                else:
                    data = f.read()
                    self.cache_record(aid, fmt, data)

    def get_cached_record(self, aid, fmt): 
        if fmt=='orig': fmt = 'zip'
        data = self.records.get(aid,{}).get(fmt)
        if data is None: # look for cache on disk
            self._load_activity(aid, fmt)
            data = self.records.get(aid,{}).get(fmt)
        return data

    def __iter__(self):
        for i,a in enumerate(self.sum):
            if i >= len(self.activities):
                self._load_activity(a['id'])
            yield self.activities[i]

    def __getitem__(self, key):
        if key >= len(self.activities) and key < len(self.sum):
            print(len(self.activities), key+1)
            for i in range(len(self.activities), key+1):
                self._load_activity(self.sum[i]['id'])
        return self.activities[key]

    def clear_cache(self, everything=False, activities=False, records=False):
        "clear some part of cache"
        if activities or everything:
            self.sum=[]
            self.activities = []    
        if records or everything:
            self.records = {}

    def update(self):
        if not self.sum:
            self.download_activities(getAll=True)
        else:
            # improve filtering to get activities from certain commit time
            # we nainvely re-download activitiues till we get all we need
            # we'll download ALL activities in case the latest one was deleted, it will stay cached on disk if its there, but summary will be cleaned
            need=10
            lastest_id = self.sum[0]['id']
            tmpsum = self.sum
            while need>0:
                self.download_activities(need)
                for i,act in enumerate(self.activities):
                    if lastest_id == act['activity']['activityId']:
                        self.activities = self.activities[:i] # rest will come from cache, TODO is it ok?
                        self.sum = self.sum[:i]
                        self.sum.extend(tmpsum)
                        need = 0
                        break
                if len(self.activities) != need:
                    break
                if need == 10:
                    need = self.gc_max_req_limit
                elif need>0:
                    need += self.gc_max_req_limit
        self.save()

    def save(self, only_aid=None):
        "if aid set, set particular activity id only"
        if only_aid is None:
            # save sum file
            if self.v: print("Saving activity summary to ", self.sum_file)
            with open(self.sum_file, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=[x for x in self.sum[0].keys()])
                writer.writeheader()
                for s in self.sum:
                    writer.writerow(s)

        # save individual acitivities, but only ones downloaded
        for act in self.activities:
            aid = act['activity']['activityId']
            if only_aid is not None and aid != only_aid:
                continue

            adir = os.path.join(self.cache_dir, aid)
            if not os.path.isdir(adir):
                os.mkdir(adir)

            ajsonf = os.path.join(adir, aid+'.json')
            if not os.path.isfile(ajsonf):
                if self.v: print("Saving activity id", aid,">> details")
                with open(ajsonf, 'w') as f:
                    f.write(json.dumps(act, indent=4))
                    #f.write(pprint.pformat(act))

        # save downloaded records
        for aid, recs in self.records.items():
            if only_aid is not None and aid != only_aid:
                continue

            adir = os.path.join(self.cache_dir, aid)
            if not os.path.isdir(adir):
                os.mkdir(adir)

            for k, v in recs.items():
                if k=='orig': k = 'zip'
                acf = os.path.join(adir, aid+'.'+k)
                if not os.path.isfile(acf):
                    if self.v: print("Saving activity id",aid,">>",k,"record")
                    openlike = 'w' if isinstance(v, str) else 'wb'
                    with open(acf, openlike) as f:
                        f.write(v)


