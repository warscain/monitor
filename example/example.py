#!/usr/bin/python
# coding = UTF-8

import threading,re,time,sys,os
from subprocess import *
from shlex import split

#global Variables
prev_cpu_info = {"user":0,"system":0,"idle":0,"iowait":0}
cpu_stat = []
prev_partition_info = []
HZ = 100
SLEEP_TIME = 3
prev_net_info = {"in":0,"out":0}

class SysMonitor(threading.Thread):
    def __init__(self,name,eventList,eventListMutex):
        threading.Thread.__init__(self)
        self.name = name
        self.eventList = eventList
        self.eventListMutex = eventListMutex
        self.running = True
        self.runningMutex = threading.Lock()

    def stop(self):
        self.runningMutex.acquire()
        self.running = False
        self.runningMutex.release()
    
    def calculate_deltams(self):
        ncpu = self.get_numbers_of_cpu()    
    
        if len(cpu_stat) == 0:
            raise Exception("Please run check_cpu() at first!")

        deltams = 1000.0 * ((cpu_stat['user'] + cpu_stat['system'] + cpu_stat['idle'] + cpu_stat['iowait']) - (prev_cpu_info['user'] + prev_cpu_info['system'] + prev_cpu_info['idle'] + prev_cpu_info['iowait'])) / ncpu / HZ

        return deltams

    def get_numbers_of_cpu(self):
        try:
            cpufp = file("/proc/cpuinfo")
            ncpu = 0
            while True:
                line = cpufp.readline()
                if len(line) < 1:
                    break
                if re.search(r"processor\t:",line) != None:
                    ncpu += 1
        finally:
            cpufp.close()
        return ncpu

    def get_cpu_stat(self):
        cpu_info = {
            "user"    :    0,
            "system":    0,
            "idle"    :    0,
            "iowait":    0
        }

        try:
            cpustatfp = file("/proc/stat")
            line = split(cpustatfp.readline())
            cpu_info['user'] = float(line[1]) + float(line[2])
            cpu_info['system'] = float(line[3]) + float(line[6]) + float(line[7])
            cpu_info['idle'] = float(line[4])
            cpu_info['iowait'] = float(line[5])

        finally:
            cpustatfp.close()
    
        return cpu_info

    def check_cpu(self):
        global prev_cpu_info,cpu_stat
        cpu = {
            "user"    :    0,
            "system":    0,
            "idle"    :    0,
            "iowait":    0
        }
    
        if prev_cpu_info['system'] == 0:
            prev_cpu_info = self.get_cpu_stat()
            time.sleep(1)
        else:
            prev_cpu_info = cpu_stat
    
        cpu_stat = self.get_cpu_stat()

        cpu['user'] = cpu_stat['user'] - prev_cpu_info['user']
        cpu['system'] = cpu_stat['system'] - prev_cpu_info['system']
        cpu['idle'] = cpu_stat['idle'] - prev_cpu_info['idle']
        cpu['iowait'] = cpu_stat['iowait'] - prev_cpu_info['iowait']
    

        total = (cpu['user'] + cpu['system'] + cpu['idle'] + cpu['iowait'] ) 

        cpu['user'] = cpu['user'] / total * 100
        cpu['system'] = cpu['system'] / total * 100
        cpu['idle'] = cpu['idle'] / total * 100
        cpu['iowait'] = cpu['iowait'] / total * 100
        
        return cpu

    def get_disk_stat(self):
        diskfp = open('/proc/diskstats')
        all_partition = []
        curr = {
            "major":0,
            "minor":0,
            "name" : None,            #disk name
            "rd_ios" : 0,            #read I/O operation
            "rd_merges" : 0,        #readed merged
            "rd_sectors" : 0,        #sectors readed
            "rd_ticks" : 0,            #time in queue and server for read
            "wr_ios" : 0,            #write I/O operation
            "wr_merges" : 0,        #write merged
            "wr_sectors" : 0,        #sectors writed
            "wr_ticks" : 0,            #time in queue and server for write
            "ticks" : 0,            #time of request in queue
            "aveq" : 0                #average queue length
        }
        while True:
            line = split(diskfp.readline())
            if len(line) == 0:
                break
            if int(line[3]) == 0:
                continue
            curr['major'] = line[0]
            curr['minor'] = line[1]
            curr['name'] = line[2]
            curr['rd_ios'] = float(line[3])
            curr['rd_merges'] = float(line[4])
            curr['rd_sectors'] = float(line[5])
            curr['rd_ticks'] = float(line[6])
            curr['wr_ios'] = float(line[7])
            curr['wr_merges'] = float(line[8])
            curr['wr_sectors'] = float(line[9])
            curr['wr_ticks'] = float(line[10])
            curr['ticks'] = float(line[11])
            curr['aveq'] = float(line[12])

            all_partition.append(curr.copy())    

        return all_partition

    def check_disk(self):
        global prev_partition_info
        DISK_STAT = []
        deltams = self.calculate_deltams()

        curr_partition_info = self.get_disk_stat()
        if len(prev_partition_info) == 0:
            prev_partition_info = curr_partition_info
            curr_partition_info = self.get_disk_stat()

        partition_num = len(curr_partition_info)
        i = 0
        while i < partition_num:
            disk_info = curr_partition_info[i]
            prev_disk_info = prev_partition_info[i]

            rd_ios = disk_info['rd_ios'] - prev_disk_info['rd_ios']
            rd_merges = disk_info['rd_merges'] - prev_disk_info['rd_merges']
            rd_sectors = disk_info['rd_sectors'] - prev_disk_info['rd_sectors']
            rd_ticks = disk_info['rd_ticks'] - prev_disk_info['rd_ticks']
            wr_ios = disk_info['wr_ios'] - prev_disk_info['wr_ios']
            wr_merges = disk_info['wr_merges'] - prev_disk_info['wr_merges']
            wr_sectors = disk_info['wr_sectors'] - prev_disk_info['wr_sectors']
            wr_ticks = disk_info['wr_ticks'] - prev_disk_info['wr_ticks']
            ticks = disk_info['ticks'] - prev_disk_info['ticks']
            aveq = disk_info['aveq'] - prev_disk_info['aveq']
    
        #    prev_disk_info = disk_info        #store the old info
            prev_partition_info[i] = curr_partition_info[i]
            i = i + 1
            n_ios = rd_ios + wr_ios
            n_ticks = rd_ticks + wr_ticks
            n_kbytes = (rd_sectors + wr_sectors) / 2.0

            queue = aveq / deltams
            if n_ios:
                size = n_kbytes / n_ios
                wait = n_ticks / n_ios
            else:
                size = 0.0
                wait = 0.0    
    
            busy = 100.0 * ticks / deltams

            if busy > 100.0:
                busy = 100
    
        #    print rd_sectors,wr_sectors
    
            readPerSec = str(1000 * rd_sectors / deltams / 2.0 * 1024)
            writePerSec = str(1000.0 * wr_sectors / deltams / 2.0 * 1024)

            readPerSec = readPerSec[:readPerSec.find(".") + 3]
            writePerSec = writePerSec[:writePerSec.find(".") + 3]
            

            #calculate total size and free size for every partition
            try:
                mounts = open("/etc/mtab")
                #initialize
                total_size = 0
                free_size = 0
                while True:
                    line = mounts.readline().strip()
                    if len(line) <1:
                        break
                    if line.find(disk_info['name'] + " ") != -1:
                        line = line.split()
                        s = os.statvfs(line[1])
                        total_size = s.f_bsize * s.f_blocks            #unit :    bytes
                        free_size = s.f_bsize * s.f_bavail            #
                        break

            finally:
                mounts.close()

            DISK_STAT.append({"name":disk_info["name"],"total_size":total_size,"free_size":free_size,"readPerSec":readPerSec,"writePerSec":writePerSec,"wait":wait,"queue":queue,"size":size})

        return DISK_STAT

    def get_net_stat(self,eth):
        try:
            netfp = file("/proc/net/dev")
            while True:
                line = netfp.readline()
                if re.search(eth,line) != None:
                    line = split(line[7:])
                    netin = int(line[0])
                    netout = int(line[8])
                    break
        finally:
            netfp.close()

        return netin,netout

    def checkNet(self):
        global prev_net_info
        NET_STATS = []
        net_stat = self.get_net_stat('wlan0')        #Caution!!! This should be the Ethernet card in use!!!

        if prev_net_info['in'] == 0 and prev_net_info['out'] == 0:
            prev_net_info['in'] = net_stat[0]
            prev_net_info['out'] = net_stat[1]

        NET_STATS.append((net_stat[0] - prev_net_info['in']) / SLEEP_TIME )
        NET_STATS.append((net_stat[1] - prev_net_info['out']) / SLEEP_TIME )
        
        prev_net_info['in'] = net_stat[0]
        prev_net_info['out'] = net_stat[1]

        return NET_STATS

    def checkMem(self):

        #the memory status file 
        MEM_FILE="/proc/meminfo"
    
        #default status
        MEM_STATUS={
            "MemTotal":0,
            "MemFree":0,
            "Cached":0,
            "SwapCached":0,
            "Active":0,
            "Inactive":0,
            "Inact_dirty":0,
            "Inact_clean":0,    
            "HighTotal":0,        
            "LowTotal":0,
            "SwapTotal":0,
            "SwapFree":0
        }

        try:
            fd = file(MEM_FILE,"r")
            mem_info_list = fd.readlines()
            PATTERN = re.compile(r"^(\w+):\s*(\d+)\s*(\w+)")    #e.g:MemTotal:        2061480 kB
            for line in mem_info_list:
                #DEBUG
                res = PATTERN.match(line)
                if res:
                    var_list = res.groups()
                    if MEM_STATUS.has_key(var_list[0]):
                        MEM_STATUS[var_list[0]] = var_list[1]
            fd.seek(0)
        finally:
            fd.close()

        return MEM_STATUS


    def run(self):
        while True:    
            self.runningMutex.acquire()
            if not self.running:
                self.runningMutex.release()
                break
            self.runningMutex.release()

            cpuStatus = self.check_cpu()
            diskStatus = self.check_disk()
            netStatus = self.checkNet()
            memStatus = self.checkMem()
            
            #add those status to eventList
        #    print cpuStatus
        #    print memStatus
        #    print diskStatus
        #    print netStatus
            

            self.eventListMutex.acquire()
            while len(self.eventList) > 0:
                del self.eventList[0]
            self.eventList.append({"cpu":cpuStatus,"mem":memStatus,"disk":diskStatus,"net":netStatus})    #Changed!!! trasform the dictionary to string!!!
            self.eventListMutex.release()
            
            #Just for test
            time.sleep(SLEEP_TIME)

if __name__ == '__main__':
    monitor = SysMonitor('SysMonitor',[],threading.Lock())
    monitor.start()