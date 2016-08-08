#!/usr/bin/python

import smtplib
import os
import time
import datetime
import glob
import MySQLdb
from time import strftime



os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
temp_sensor = '/sys/bus/w1/devices/28-80000027b718/w1_slave'
 
# Variables for MySQL
db = MySQLdb.connect(host="localhost", user="root",passwd="123456789", db="temp_database")
cur = db.cursor()
 
def tempRead():
    t = open(temp_sensor, 'r')
    lines = t.readlines()
    t.close()
 
    temp_output = lines[1].find('t=')
    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string)/1000.0
    return round(temp_c,1)

threshold = 200
#don't forget to change 'above' or 'below'
while True:
    temp = tempRead() 
    print temp
    datetimeWrite = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:%S"))
    print datetimeWrite
    sql = ("""INSERT INTO tempLog (datetime,temperature) VALUES (%s,%s)""",(datetimeWrite,temp))
    try:
        print "Writing to database..."
        # Execute the SQL command
        cur.execute(*sql)
        # Commit your changes in the database
        db.commit()
        print "Write Complete"
 
    except:
        # Rollback in case there is any error
        db.rollback()
        print "Failed writing to database"

    
    #cur.close()
    #db.close()

    if tempRead() < threshold:
        strFrom = 'Your Temperature Sensor'
        strTo = 'rpiprojectrecipient@gmail.com'
        #datestr = str(datetime.datetime.utcnow())
        datestr = datetime.datetime.utcnow().strftime("%x, %X") 
        newdatestr = datestr.replace(":",".")
        msg = 'At ' + newdatestr + ' the temperature was below ' + str(threshold) + ' degrees Fahrenheit.'
        smtp = smtplib.SMTP()
        smtp.connect('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login('ds18b20sensor@gmail.com', 'celinaisawesome')
        smtp.sendmail(strFrom, strTo, msg)
        print 'email sent'

    time.sleep(3)
