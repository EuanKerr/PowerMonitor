#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import radio
import Devices
import OpenThings
import mysql.connector
from datetime import date, datetime
from time import strftime

db_host = "localhost"
db_user = "powerUser"
db_passwd = ""
db_database = "power"

APP_DELAY    = 30

def loop(receive_time=1):
    radio.receiver(fsk=True)
    timeout = time.time() + receive_time
    handled = False

    while True:
        if radio.is_receive_waiting():
            payload = radio.receive_cbp()
            now = time.time()
            try:
                msg        = OpenThings.decode(payload, receive_timestamp=now)
                hdr        = msg["header"]
                mfr_id     = hdr["mfrid"]
                product_id = hdr["productid"]
                device_id  = hdr["sensorid"]
                address    = (mfr_id, product_id, device_id)
                msg_list   = msg["recs"]
                handled = True
            except OpenThings.OpenThingsException:
                pass
                # print("Can't decode payload:%s" % payload)

        now = time.time()
        if now > timeout: break

    # print("handled: {handled}".format(handled=handled))
    if handled:
        return msg_list
    else:
        return handled

def energy_monitor_loop():
    msg = loop()

    if not msg:
	#print("pass")
        pass
    else:
        power      = msg[0]["value"]
	if power > 1000:
	    print("over 1000W")
	    return False
	if power < 20:
	    print("less than 0W")
	    return False
        voltage    = msg[2]["value"]
        frequency  = round(msg[3]["value"], 0)
        # print("Power: {power}, Voltage: {voltage}, Frequency: {frequency}".format(power=power, voltage=voltage, frequency=frequency))
        # print("{power}, {voltage}, {frequency}".format(power=power, voltage=voltage, frequency=frequency))
        try:
            sqlConn = mysql.connector.connect(host=db_host, user=db_user, passwd=db_passwd, db=db_database)
            sqlCursor = sqlConn.cursor()
        except Exception, e:
            print "{}: Unexpected error 2 (connecting to DB): {}".format(datetime.now(), e)
            return

        try:
            sqlCursor.execute("INSERT INTO server_power (powerTime, powerDate, powerValue, voltageValue, frequencyValue) VALUES(%s,%s,%s,%s,%s)", (strftime("%Y-%m-%d %H:%M:%S"), date.today(), power, voltage, frequency))
            sqlConn.commit()
        except Exception, e:
            print "{}: Unexpected error 1 (Inserting into DB): {}".format(datetime.now(), e)
        sqlConn.close()
        return True

    # time.sleep(APP_DELAY)
    return False


if __name__ == "__main__":

    radio.init()
    OpenThings.init(Devices.CRYPT_PID)

    try:
        while energy_monitor_loop() is False:
            energy_monitor_loop()
    finally:
        radio.finished()

