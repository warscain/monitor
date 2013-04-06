#!/usr/bin/python
# coding = UTF-8
# hardware_info.py

import re
import commands
import tempfile
import os



# 
# class hardware(object):
# 
#     def __init__(self):
#         pass
# 
#     def bios(self):
#         bios_tmp = commands.getstatusoutput('dmidecode -t bios')
#         print bios_tmp
#         bios_vendor_cmp = re.compile('Vendor: (.*)\n')
#         bios_version_cmp = re.compile('Version: (.*)\n')
#         bios_revision_cmp = re.compile('BIOS Revision: (.*)\n')
#         bios_firmware_revision_cmp = re.compile('Firmware Revision: (.*)\n')
#         bios_characteristics_cmp_0 = re.compile('Characteristics:\n((\t{2}.*\n)*)')
#         bios_characteristics_cmp_1 = re.compile('\t{2}(.*)\n')
# 
#         bios_vendor = re.search(bios_vendor_cmp, bios_tmp[1]).group(1)
#         bios_version = re.search(bios_version_cmp, bios_tmp[1]).group(1)
#         bios_revision = re.search(bios_revision_cmp, bios_tmp[1]).group(1)
#         bios_firmware_revision = re.search(bios_firmware_revision_cmp, bios_tmp[1]).group(1)
#         bios_characteristics_0 = re.search(bios_characteristics_cmp_0, bios_tmp[1]).group(1)
#         bios_characteristics_1 = re.findall(bios_characteristics_cmp_1, bios_characteristics_0)
# 
#         return bios_vendor, bios_version, bios_revision, bios_firmware_revision, bios_characteristics_1, 
# 
# aaa = hardware()
# for section in aaa.bios():
#     print section

def dmi_parser(device):
#dmi_list example:
#    dmi_list = [ [title1,[ [xxx, [a] 
#                             ],
#                             [yyy, [a,b,c]
#                             ],
#                           ]
#                 ],
#                 [title2,[]],
#               ]
    dmi_rst = commands.getstatusoutput('dmidecode -t ' + device)
    if dmi_rst[0] == 0:
        dmi_tmpfile = tempfile.mktemp(prefix='dmi_parser', dir='/tmp')
        tmpfile_fh = open(dmi_tmpfile, 'w+') 
        tmpfile_fh.write(dmi_rst[1])
        tmpfile_fh.flush()
        tmpfile_fh.seek(0)

        mul_section = []
        dmi_list = []
        line_num = 0
        for line in tmpfile_fh:
            line_num += 1
            if line_num > 3:
                if re.match('\w+', line) and not line.startswith('Handle'):
                    title = line.strip()
                    dmi_list.append([title,[]])
                if re.match('\t\w+', line):
                    section = line.lstrip().split(':')
                    item = section[0]
                    value = section[1].strip()
                    if item and value:
                        mul_section = ''
                        dmi_list[-1][1].append([item,[value]])
                    else:
                        mul_section = [item,[]]
                        dmi_list[-1][1].append(mul_section)
                if re.match('\t\t\w+', line):
                    dmi_list[-1][1][-1][1].append(line.strip())

        os.remove(dmi_tmpfile)
    print dmi_list
    return dmi_list


def test(device):
    all = dmi_parser(device)
    for title_result in all:
        print '='*5, title_result[0], '='*5
        for item in title_result[1]:
            print item

test('bios')
# test('system')
# test('baseboard')
# test('chassis')
# test('processor')
# test('memory')
# test('cache')
# test('connector')
# test('slot')



















