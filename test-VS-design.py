import requests
import argparse
import time
import json
import datetime
import urllib
import ssl
from avi.sdk.avi_api import ApiSession

def get_events_for_vs(api, vs):
    today_date=urllib.quote(datetime.datetime.now().isoformat()+"Z")
    url = ('analytics/logs/'
            '?type=2'
            '&duration=864000'
            '&filter=co(all,%s)'
            '&end=%s'
            '&orderby=-report_timestamp'
            '&page=1'
            '&page_size=30'
            %(vs,today_date))
    #print url
    events = api.get(url).json()['results']
    print "\n VS Events : ========= %s \n"%(vs)

    for event in events:
            print (event['report_timestamp'] + "====>" + event['event_description'])



    #VS1=api.get_object_by_name("virtualservice",'VS2')


if __name__ == "__main__":
    gcontext = ssl._create_unverified_context()

    requests.packages.urllib3.disable_warnings()
    parser = argparse.ArgumentParser(
        description="Script to get the config logs from Avi controller")
    parser.add_argument("-u", "--username", required=True,
                        help="Login username")
    parser.add_argument("-p", "--password", required=True,
                        help="Login password")
    parser.add_argument("-c", "--controller", required=True,
                        help="Controller IP address")
    parser.add_argument("-v", "--vs", required=False,
                        help="VirtualService uuid for which config logs are"
                             " needed. If not specified, config logs for all "
                             "VSes are fetched.")
    args = parser.parse_args()
    today_date=urllib.quote(datetime.datetime.now().isoformat()+"Z")

    api = ApiSession.get_session(args.controller, args.username, args.password, tenant="admin", api_version="18.2.4")
    vs_uuid = api.get_object_by_name("virtualservice",args.vs)['uuid']
    VS1=api.get_object_by_name("virtualservice",'VS2')['vip_runtime'][0]['se_list']
    for se in VS1:
        k=[]
        k.append(se['se_ref'])
        se_id=k[0].split('/')
        se_ref_id=se_id[-1]
        se_ref_uuid = se_ref_id.encode("utf-8")
        se_actual_name=api.get('serviceengine/' + se_ref_uuid).json()
        se_name=se_actual_name['name']
        se_analytics_url =('analytics/logs'
        '?type=2'
        '&page_size=10000'
        '&filter=co(all,%s)'
        '&end=%s'
        '&duration=864000'
        %(se_ref_uuid ,today_date))
        events1 = api.get(se_analytics_url).json()['results']
        print '\nEvents for :=== %s \n' %(se_name)
        for events in events1:

            print  (events['report_timestamp'] + "+++++" + events['event_description'])
            details = events['event_details']
            description = events['event_description']
            for key, value in details.iteritems():
                if type(details[key]) is dict:
                    #print events[key]
                    if 'reason' in details[key].keys():
                        #print "Found Reason for the Event %s" % str(description)
                        print "Reason is %s\n" % str(details[key]['reason'])
        #print 'Events for :=== %s \n' %(se_name)
        #for event_res in events1:
            #print  event_res['report_timestamp'] + "+++++" + event_res['event_description']

if args.vs:
        get_events_for_vs(api, vs_uuid)
else:
        get_config_logs_for_all_vses(api)
