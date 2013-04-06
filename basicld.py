#!/usr/bin/python
# coding = UTF-8

import commands

class performance_base(object):

    def avg_load(self):
        '''os avg load, return a tuple include 2 list like (['0.03', '0.17', '0.15'], ['2', '437'])'''
        os_load_fh = open('/proc/loadavg', 'r')
        self.os_load_filelines = os_load_fh.readlines()
        os_load_fh.close()

        line = self.os_load_filelines[0]
        tmplist =  line.rstrip().split()
        tmplist[3] = tmplist[3].split('/')
        avg_load = tmplist[:3]
        process_load = tmplist[3]
        return (avg_load, process_load)

    def mem_ratio(self):
        mem_tmp = commands.getstatusoutput('free')
        mem_tmp_list = mem_tmp[1].split()
        mem_total = int(mem_tmp_list[7]) / 1024.0
        mem_used = int(mem_tmp_list[8]) / 1024.0
        mem_free = int(mem_tmp_list[9]) / 1024.0
        mem_real_use = int(mem_tmp_list[15]) / 1024.0
        mem_real_free = int(mem_tmp_list[16]) / 1024.0
        mem_ratio = float(mem_used) / mem_total * 100
        mem_ratio_real = float(mem_real_use) / mem_total * 100
        swap_total = int(mem_tmp_list[18]) / 1024
        swap_used = int(mem_tmp_list[19]) / 1024
        swap_free = int(mem_tmp_list[20]) / 1024
        if swap_total == 0:
            swap_ratio = 0
        else:
            swap_ratio = float(swap_used) / swap_total * 100
        return (mem_total,
                 mem_used,
                 mem_free,
                 mem_real_use,
                 mem_real_free,
                 mem_ratio,
                 mem_ratio_real,
                 swap_total,
                 swap_used,
                 swap_free,
                 swap_ratio)


aaa =performance_base()
print aaa.avg_load()
print aaa.mem_ratio()


