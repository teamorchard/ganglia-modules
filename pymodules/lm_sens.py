#!/usr/bin/env python
'''
ganglia/gmond python module to use lm-sensors to inject some fan and temp
info into ganglia.

Reference:

https://github.com/ganglia/monitor-core/blob/master/gmond/modules/python/README.in

'''

import subprocess

def get_it():
    string = subprocess.check_output("sensors -u", shell=True)
    ret = dict()
    cur_device = None
    cur_adapter = None
    cur_thing = None
    for line in string.split('\n'):
        if not line.strip():
            cur_device = None
            cur_adapter = None
            cur_thing = None
            continue

        if not cur_device:
            cur_device = line.strip()
            ret[cur_device] = dict()
            continue

        if not cur_adapter:
            cur_adapter = line.strip().split(':')[1].strip()
            ret[cur_device][cur_adapter] = dict()
            continue

        if not line.startswith(' '): # new thing
            cur_thing = line.strip().split(':')[0].strip()
            ret[cur_device][cur_adapter][cur_thing] = dict()
            continue


        name,num = line.strip().split(':')
        num = int(float(num))
        #print "%s:%s:%s:%s = %.0f" % (cur_device, cur_adapter, cur_thing, name, num)
        ret[cur_device][cur_adapter][cur_thing][name] = num
        continue
    return ret

registered = dict()

def pick_it(name):
    global registered
    what = registered[name]
    #print "-> %s: '%s'" % (name, what)
    dev, ada, thing, name = what.split(':')
    dat = get_it()
    try:
        ret = dat[dev][ada][thing][name]
    except KeyError:
        #print dat[dev][ada][thing]
        raise
    #print "%s: %s:%s:%s:%s = %.0f" % (name, dev, ada, thing, name, ret)
    return ret

defaults = dict(
    name = '',                       # override this
    units = '',                      # override this
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
    for pname,pvar in params.items():
        dev, ada, thing, name = pvar.split(':')
        units = ''
        if name.startswith('temp'):
            units = 'C'
        if name.startswith('fan'):
            units = 'RPM'
        one = dict(defaults, name = pname, units = units, 
                   description = '%s: %s' % (thing,name),
                   call_back = pick_it)
        registered[pname] = pvar
        #print "<- %s: '%s'" % (pname, pvar)
        desc.append(one)
    return desc
                   
def metric_cleanup():
    pass




# do some local testing
if '__main__' == __name__:

    # run "sensors -u" to see what to put here
    param = dict(
        Core0Temp = "coretemp-isa-0000:ISA adapter:Core 0:temp2_input",
        Core1Temp = "coretemp-isa-0000:ISA adapter:Core 1:temp3_input",
        Core2Temp = "coretemp-isa-0000:ISA adapter:Core 2:temp4_input",
        Core3Temp = "coretemp-isa-0000:ISA adapter:Core 3:temp5_input",
        CPUTemp = "coretemp-isa-0000:ISA adapter:Physical id 0:temp1_input",
        Fan1 = "nct6791-isa-0290:ISA adapter:fan1:fan1_input",
        Fan2 = "nct6791-isa-0290:ISA adapter:fan2:fan2_input",
        Fan3 = "nct6791-isa-0290:ISA adapter:fan3:fan3_input",
        Fan4 = "nct6791-isa-0290:ISA adapter:fan4:fan4_input",
        Fan5 = "nct6791-isa-0290:ISA adapter:fan5:fan5_input",
        Fan6 = "nct6791-isa-0290:ISA adapter:fan6:fan6_input",
    )
    descriptors = metric_init(param)

    for d in descriptors:
        n = d['name']
        v = d['call_back'](n)
        print 'value for %s is %u %s' % (n, v, d['units'])

        
    
