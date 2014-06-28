#!/usr/bin/env python
'''
ganglia/gmond python module to use hddtemp hard drive temperature
info into ganglia.

Reference:

https://github.com/ganglia/monitor-core/blob/master/gmond/modules/python/README.in

'''

import subprocess

import socket

configuration = dict(host='localhost',port=7634)


def get_it_net():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((configuration['host'], configuration['port']))
    string = ""
    while True:
        d = sock.recv(1024)
        if d == "":
            break
        string += d
        continue
    sock.close()
    ret = dict()
    # |dev|Maker Model|Temp|Unit||...||...|
    for ds in string.split('||'):
        parts = ds.strip('|').split('|')
        dev,model,temp,unit = parts
        ret[dev] = int(temp)
    return ret

registered = dict()
def pick_it(name):
    global registered
    dev = registered[name]
    return get_it_net()[dev]

defaults = dict(
    name = '',                       # override this
    units = 'C',                     # override this
    description = '',                # override this
    call_back = None,
    time_max = 600,
    value_type = 'uint',
    slope = 'both',
    format = '%u',
    groups = 'thermal')

def metric_init(params):
    global registered
    desc = list()
    for name, dev in params.items():
        registered[name] = dev
        one = dict(defaults, name = name,
                   description = 'HDD %s Temperature' % (dev,),
                   call_back = pick_it)
        desc.append(one)
    return desc



# Local test
if '__main__' == __name__:

    # this would go as "param" values
    param = dict(
        SSDTemp = '/dev/sda',
        HDDTemp = '/dev/sdb',
    )
    descriptors = metric_init(param)

    for d in descriptors:
        n = d['name']
        v = d['call_back'](n)
        print 'value for %s is %u %s' % (n, v, d['units'])


