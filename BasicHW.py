#!/usr/bin/python
# coding = UTF-8
# hardware_info.py

import re
import commands

def dmi_parser(device):
    '''dmi_list example:
dmi_list = [ [title1,[ [xxx, [a] 
                         ],
                         [yyy, [a,b,c]
                         ],
                       ]
             ],
             [title2,[...]],
           ]'''
    dmi_rst = commands.getstatusoutput('dmidecode -t ' + str(device))
    if dmi_rst[0] == 0:
        dmi_out = dmi_rst[1]
        line = ''
        line_num = 0
        dmi_list = []
        mul_section = []
        for word in dmi_out:
            if not word == '\n':
                line += word
                continue
            else:
                line_num += 1
                if line_num > 3:
                    if re.match('\w+', line) and not line.startswith('Handle'):
                        title = line.strip()
                        dmi_list.append([title, []])
                    if re.match('\t\w+', line):
                        section = line.lstrip().split(':')
                        item = section[0]
                        value = section[1].strip()
                        if item and value:
                            mul_section = ''
                            dmi_list[-1][1].append([item, [value]])
                        else:
                            mul_section = [item, []]
                            dmi_list[-1][1].append(mul_section)
                    if re.match('\t\t\w+', line):
                        dmi_list[-1][1][-1][1].append(line.strip())
                line = ''
    print dmi_list # debug
    return dmi_list

def test(device):
    for title_result in dmi_parser(device):
        print '='*5, title_result[0], '='*5
        for item in title_result[1]:
            print item

# test('bios')
# test('system')
# test('baseboard')
# test('chassis')
test('processor')
# test('memory')
# test('cache')
# test('connector')
# test('slot')
 
# for num in range(0,256):
#     print num, test(num)
















