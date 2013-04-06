#!/usr/bin/python
# coding = UTF-8
# hardware_info.py

import re
import commands

class hardware(object):

    def __init__(self):
        pass

    def os_info(self):
        kernel_release = commands.getstatusoutput('uname -r')
        machine_arch = commands.getstatusoutput('uname -m')
        hardware_arch = commands.getstatusoutput('uname -i')
        cpu_arch = commands.getstatusoutput('uname -p')
        host_name = commands.getstatusoutput('uname -n')
        os_time = commands.getstatusoutput('LANG=C date +%Y/%m/%d/%H:%M:%S/%w/%V')
        return kernel_release, machine_arch, hardware_arch, cpu_arch, host_name, os_time

    def cpu_info(self):
        cpu_name_fh = open('/proc/cpuinfo', 'r')

        model_cmp = re.compile('^(model\ name)\s+:\s+(.*)\n')
        core_number_cmp = re.compile('^(cpu\ cores)\s+:\s+(.*)\n')
        logical_number_cmp = re.compile('^(processor)\s+:\s+(.*)\n')
        socket_number_cmp = re.compile('^(physical\ id)\s+:\s+(.*)\n')

        model_name = None
        core_number = None
        logical_core_number = None
        socket_number = None

        for line in cpu_name_fh:
            model_name_search = re.search(model_cmp, line)
            core_number_search = re.search(core_number_cmp, line)
            logical_core_number_search = re.search(logical_number_cmp, line)
            socket_number_search = re.search(socket_number_cmp, line)

            if model_name_search:
                model_name = model_name_search.group(2)
            if core_number_search:
                core_number = int(core_number_search.group(2))
            if logical_core_number_search:
                logical_core_number = int(logical_core_number_search.group(2)) + 1
            if socket_number_search: 
                socket_number = int(socket_number_search.group(2)) + 1
        
        cpu_name_fh.close()

        return (model_name,
                 core_number,
                 logical_core_number,
                 socket_number)

    def mem_info(self):
        mem_tmp = commands.getstatusoutput('free')
        mem_tmp_list = mem_tmp[1].split()
        mem_total = int(mem_tmp_list[7])/1024.0
        return str(mem_total)

    def disk_info_root(self):
        disk_tmp = commands.getstatusoutput('fdisk -l')
        disk_cmp = re.compile('Disk\s+(.*):\s+(.*)\s+([A-Z]{2})')
        disk_info_all = []
        for item in disk_tmp:
            disk_search = re.finditer(disk_cmp, str(item))
            for item in disk_search:
#                print item.group(1), item.group(2), item.group(3)
                disk_info_all.append([item.group(1), [item.group(2), item.group(3)]])
        return disk_info_all

    def disk_info_noroot(self):
        disk_tmp = open('/proc/partitions')
        disk_cmp = re.compile('^\s+\d+\s+\d+\s+(\d+)\s+(\w+)\n')
        disk_name = 'temp'
        
        disk_info_all = []
        for line in disk_tmp:
            disk_search = re.search(disk_cmp, line)
            if disk_search:
                if disk_name in disk_search.group(2):
                    continue
                else:
                    disk_name = disk_search.group(2)
                    disk_size = float(disk_search.group(1))/1024.0/1024.0
                    disk_info_all.append([disk_name, disk_size])
        return disk_info_all



aaa = hardware()
print aaa.os_info()

print aaa.cpu_info()
print aaa.mem_info()
print aaa.disk_info_noroot()
print aaa.disk_info_root()







#root@lucifer:~# dmidecode  |grep -P -A10 '^Memory\s+Device$'
#Memory Device
#    Array Handle: 0x0005
#    Error Information Handle: Not Provided
#    Total Width: 64 bits
#    Data Width: 64 bits
#    Size: 4096 MB
#    Form Factor: SODIMM
#    Set: None
#    Locator: ChannelA-DIMM0
#    Bank Locator: BANK 0
#    Type: DDR3
#--
#Memory Device
#    Array Handle: 0x0005
#    Error Information Handle: Not Provided
#    Total Width: 64 bits
#    Data Width: 64 bits
#    Size: 4096 MB
#    Form Factor: SODIMM
#    Set: None
#    Locator: ChannelB-DIMM0
#    Bank Locator: BANK 2
#    Type: DDR3

















