#!/usr/bin/python
import time
import random
import math 

TIME_WINDOW = 1

N_FLOWS = 5

T_MAX = 3 * TIME_WINDOW

flow_results_db = {}

N_SIGMA = 2


def read_flows(T) :
    print "reading flows"
    for i in range(0, N_FLOWS):
        #select if flow is ok or not
        
        if (T < T_MAX ):
            flow_results_db[i]['timestamp'].append( time.time() )
            flow_results_db[i]['packets_per_second'].append( i + random.randint( i-1, i+1)  )
            flow_results_db[i]['bytes_per_second'].append( 100*( i + random.randint( i-1, i+1) ) )
        else:
            print "Creating dangerous flows"
            flow_results_db[i]['timestamp'].append( time.time() )
            flow_results_db[i]['packets_per_second'].append( 2*(i + random.randint( i-1, i+1) )  )
            flow_results_db[i]['bytes_per_second'].append( 200*( i + random.randint( i-1, i+1) ) )

#def mean function 
def mean(values):
    return sum(values)*1.0/len(values)

#def standard deviation mean
def stanDev(values):
	length=len(values)
	m=mean(values)
	total_sum=0
	for i in range (0,length):
	    total_sum+= (values[i]-m)**2
	under_root=total_sum*1.0/length
	return math.sqrt(under_root)
	
def check_flow(flow_id):

    #check pkts_per_sec
    check_flow_param(flow_id, 'packets_per_second' )

    #check bytes_per_sec
    check_flow_param(flow_id, 'bytes_per_second' )

def check_flow_param(flow_id, param) :
    values = flow_results_db[i][param][0:-1]
    print values
    if len(values) < 2 :
        return True
    #condicion
    print "Flow: " + str(flow_id) + " Current param " + param + " mean: " + str(mean(values)) + " stanDev: " + str(stanDev(values))
    threshold = mean(values)+N_SIGMA*stanDev(values)

    print "Flow: " + str(flow_id) + " Current param " + param + " value: " + str(flow_results_db[i][param][-1]) + " threshold: " + str(threshold)

    if flow_results_db[i][param][-1] >  threshold:
        print "Security warning in Flow " + str(flow_id) + " parameter: " + param
        exit()
    return True

def process_flows():
    for i in range(0, N_FLOWS):
        check_flow(i)


    
if __name__ == '__main__':
    print "SECURITY APP"
    T = 0
    #INIT
    for i in range(0, N_FLOWS):
        flow_results_db[i] = { 'timestamp' : [], 'packets_per_second' : [], 'bytes_per_second' : [] }
    
    #START FLOW LOOP
    while(True):
        read_flows(T)
        process_flows()
        time.sleep(TIME_WINDOW)
        T += TIME_WINDOW

