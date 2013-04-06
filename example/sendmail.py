#!/usr/bin/python
# -*- coding: utf-8 *-*

localip=$(ifconfig eth0 | grep 'inet addr' | awk '{print $2}' | cut -f2 -d:)
空闲cpu由mpstat获得
cpuidle=$(mpstat | grep all | awk '{print $11}')
内存使用情况由free获得
freemem=$(free | grep Mem | awk '{print $4}')
totalmem=$(free | grep Mem | awk '{print $2}')
pcent=$(free | grep Mem | awk '{print $4/$2}')
AlertPcent=0.1
AlertCpu=10
msg=
Subject='服务器超载警报'

mailto(){
    echo $msg | mail -s $Subject $To
    python sendmail.py $Subject $msg
}

localip=$(ifconfig eth0 | grep 'inet addr' | awk '{print $2}' | cut -f2 -d:)
cpuidle=$(mpstat | grep all | awk '{print $11}')
freemem=$(free | grep Mem | awk '{print $4}')
totalmem=$(free | grep Mem | awk '{print $2}')
pcent=$(free | grep Mem | awk '{print $4/$2}')
echo $localip
echo $cpuidle
echo $freemem
echo $totalmem
echo $pcent

if [ $(echo "$pcent <= $AlertPcent"|bc) = 1 -o $(echo "$cpuidle <= $AlertCpu"|bc) = 1 ]; then
    msg='cpu空闲时间为'$cpuidle'%,可用内存剩余'$freemem',总内存为'$totalmem',剩余内存占比'$pcent'，低于10%'
    echo $msg
    mailto
else
    echo '系统运行正常'
fi


2. 空闲cpu小于cpu报警阈值或空闲内存比例低于内存报警阈值时发送邮件报警
import smtplib 
import sys
from email.mime.text import MIMEText 
 
mailto_list=[""] 
 
mail_host = "smtp.126.com" 
mail_user = "monitor_algo" 
mail_pass = "" 
mail_postfix="126.com" 
 
def send_mail(to_list, sub, context): 
    me = mail_user + "<"+mail_user+"@"+mail_postfix+">" 
    msg = MIMEText(context) 
    msg['Subject'] = sub 
    msg['From'] = me 
    msg['To'] = ";".join(to_list) 
    try: 
        send_smtp = smtplib.SMTP() 
        send_smtp.connect(mail_host) 
        send_smtp.login(mail_user, mail_pass) 
        send_smtp.sendmail(me, to_list, msg.as_string()) 
        send_smtp.close() 
        return True 
    except (Exception, e): 
        print(str(e)) 
        return False 

if __name__=="__main__":
    print ("start") 
    for a in range(1, len(sys.argv)):
        print sys.argv[a]
    if (True == send_mail(mailto_list,sys.argv[1],sys.argv[2])): 
        print ("sucess")
    else: 
        print ("failed")
