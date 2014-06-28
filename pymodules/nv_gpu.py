#!/usr/bin/env python
'''
ganglia/gmond python module to use nvidia-smi to inject some GPU
info into ganglia.

Reference:

https://github.com/ganglia/monitor-core/blob/master/gmond/modules/python/README.in

'''

import subprocess

def get_it(name):
    query = name.lower().replace('_','.')
    cmd = 'nvidia-smi --query-gpu=%s --format=csv,noheader'%query
    string = subprocess.check_output(cmd, shell=True)
    return int(string.split()[0])


defaults = dict(
    name = 'Default',                # override this
    units = 'MiB',                   # override this
    description = 'GPU Memory Free', # override this
    call_back = get_it,
    time_max = 600,
    value_type = 'uint',
    slope = 'both',
    format = '%u',
    groups = 'gpu')

descriptors = [
    dict(defaults, name = 'Memory_Free', description = 'GPU Memory Free', units = 'MiB'),
    dict(defaults, name = 'Memory_Used', description = 'GPU Memory Used', units = 'MiB'),
    dict(defaults, name = 'Memory_Total', description = 'GPU Memory Total', units = 'MiB'),
    dict(defaults, name = 'Temperature_GPU', description = 'GPU Temperature', units = 'C'),
    dict(defaults, name = 'Fan_Speed', description = 'GPU Fan Speed', units = '%'),
]

def metric_init(params):
    return descriptors

def metric_cleanup():
    '''Clean up the metric module.'''
    pass
 
#Testing
if __name__ == '__main__':
    metric_init({})
    for d in descriptors:
        n = d['name']
        v = d['call_back'](n)
        print 'value for %s is %u %s' % (n, v, d['units'])
    
