#!/usr/bin/python

import time
import random

TIME_WINDOW = 1

N_FLOWS = 5

T_MAX = 5 * TIME_WINDOW

flow_results_db = {}
def read_flows(T) :
    print "reading flows"
    for i in range(0, N_FLOWS):
        if (T < T_MAX ):
            flow_results_db[i]['timestamp'].append( time.time() )
            flow_results_db[i]['packets_per_second'].append( i + random.randint( i-1, i+1)  )
            flow_results_db[i]['bytes_per_second'].append( 100*( i + random.randint( i-1, i+1) ) )
        else:
            flow_results_db[i]['timestamp'].append( time.time() )
            flow_results_db[i]['packets_per_second'].append( i + random.randint( i-3, i+3)  )
            flow_results_db[i]['bytes_per_second'].append( 100*( i + random.randint( i-3, i+3) ) )

def process_flows() :
    print "processing flows"
    for i in range(0, N_FLOWS):
        if len(flow_results_db[i]['packets_per_second']) > 1 :
            diff = flow_results_db[i]['packets_per_second'][-1] - flow_results_db[i]['packets_per_second'][-2]
            print diff
            if diff > 2 :
                print "Security warning in Flow " + str(i)
                exit()
    
if __name__ == '__main__':
    print "SECURITY APP"
    T = 0
    for i in range(0, N_FLOWS):
        flow_results_db[i] = { 'timestamp' : [], 'packets_per_second' : [], 'bytes_per_second' : [] }
    while(True):
        read_flows(T)
        process_flows()
        time.sleep(TIME_WINDOW)
        T += TIME_WINDOW
