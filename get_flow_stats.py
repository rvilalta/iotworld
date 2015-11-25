#!/usr/bin/python

import requests
import json
import logging
import ConfigParser
import time

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

config_log = ConfigParser.ConfigParser()
config_log.read('config.cfg')

flow_results_db = { } # { 0 : { 'timestamp' : [], 'packets_per_second' : [], 'bytes_per_second' : [] } }

flow_stats_db = { } # { 0 : { 'timestamp' : [], 'packet_count' : [], 'byte_count' : [] } }

flow_db = [ ] # { 'flow_id' : 0, 'match' : {} }

flow_index = 0

OF_SWITCH = 141009632111474

TIME_WINDOW = 10

def get_switches():
    url = config_log.get( 'security_app', 'CONTROLLER_URL') + 'switches'
    headers = {'content-type': 'application/json'}
    response = requests.get(url, data='', headers=headers)
    switches = json.loads(response.content)
    return switches

def get_flows_stats( switch ):
    url = config_log.get( 'security_app', 'CONTROLLER_URL') + 'flow/' + str(switch)
    headers = {'content-type': 'application/json'}
    response = requests.get(url, data='', headers=headers)
    flows_stats = json.loads(response.content)
    print "GETTING FLOW STATS FROM OF " + str(switch)
    #print flows_stats
    return flows_stats

def get_flow_match ( flow_id):
    for flow in flow_db :
        if flow['flow_id'] == flow_id :
            return flow['match']

def get_flow_index( flow_stats ) :
    for flow in flow_db :
        #print "Comparing"
        if flow['match'] == flow_stats['match'] :
            #print "Flow found"
            #print flow_stats['match']
            return flow['flow_id']
    #if not found, store flow
    global flow_index
    flow_index += 1
    print "New flow: " + str(flow_index)
    print flow_stats['match']
    flow_db.append( { 'flow_id' : flow_index, 'match' : flow_stats['match'] } )
    flow_stats_db[flow_index] = { 'timestamp' : [], 'packet_count' : [], 'byte_count' : [] }
    flow_results_db[flow_index] = { 'timestamp' : [], 'packets_per_second' : [], 'bytes_per_second' : [] }
    return flow_index


def store_flows_stats( flows_stats ):
    #print flows_stats[ str(OF_SWITCH) ]
    for flow_stats in flows_stats[ str(OF_SWITCH) ]:
        #print flow_stats
        flow_id = get_flow_index( flow_stats )
        print "Flow received: " + str(flow_id)
        flow_stats_db[flow_id]['timestamp'].append( time.time() )
        flow_stats_db[flow_id]['packet_count'].append( flow_stats['packet_count'] )
        flow_stats_db[flow_id]['byte_count'].append( flow_stats['byte_count'] )
    print_flow_stats_db ()
    
def print_flow_stats_db ():
    for flow in flow_stats_db:
        print "Flow: " + str(flow) + " timestamp" + str(flow_stats_db[flow]['timestamp'])
        print "Flow: " + str(flow) + " packet_count" + str(flow_stats_db[flow]['packet_count'])
        print "Flow: " + str(flow) + " byte_count" + str(flow_stats_db[flow]['byte_count'])

def process_flow_stats():
    for flow in flow_stats_db:
        if len ( flow_stats_db[flow]['timestamp'] ) > 1:       
            time_delta = flow_stats_db[flow]['timestamp'][-1] - flow_stats_db[flow]['timestamp'][-2]
            packet_count_delta = flow_stats_db[flow]['packet_count'][-1] - flow_stats_db[flow]['packet_count'][-2]
            byte_count_delta = flow_stats_db[flow]['byte_count'][-1] - flow_stats_db[flow]['byte_count'][-2]
            packets_per_second = 0.0 
            packets_per_second = packet_count_delta / time_delta
            print "Flow " + str (flow) + "match: " + str( get_flow_match (flow) )
            print "Flow " + str( flow ) + " packets per second: " + str(packets_per_second)
            bytes_per_second = 0.0 
            bytes_per_second = byte_count_delta / time_delta
            print "Flow " + str( flow ) + " bytes per second: " + str(bytes_per_second) 
            flow_results_db[flow]['timestamp'].append( time.time() )
            flow_results_db[flow]['packets_per_second'].append( packets_per_second )
            flow_results_db[flow]['bytes_per_second'].append( bytes_per_second )
            if len (flow_results_db[flow]['packets_per_second'] ) > 1 :
                print "packets_per_second " + str ( flow_results_db[flow]['packets_per_second'] )
                print "packets_per_second diff " + str ( flow_results_db[flow]['packets_per_second'][-1] - flow_results_db[flow]['packets_per_second'][-2] )
                print "bytes_per_second " + str ( flow_results_db[flow]['bytes_per_second'] )
                print "bytes_per_second diff " + str ( flow_results_db[flow]['bytes_per_second'][-1] - flow_results_db[flow]['bytes_per_second'][-2] )
            
if __name__ == '__main__':
    _LOGGER.info("SECURITY APP")
    
    switches = get_switches()
    _LOGGER.debug("Received switches: %s", json.dumps(switches) )
    while(True):

        flows_stats = get_flows_stats( OF_SWITCH )
        store_flows_stats (flows_stats)
        process_flow_stats()
        time.sleep(TIME_WINDOW)        
        #check_flows()
