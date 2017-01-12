#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import radio
import Devices
import OpenThings

APP_DELAY    = 2

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
        pass
    else:
        power      = msg[0]["value"]
        voltage    = msg[2]["value"]
        frequency  = round(msg[3]["value"], 0)
        # print("Power: {power}, Voltage: {voltage}, Frequency: {frequency}".format(power=power, voltage=voltage, frequency=frequency))
        print("{power}, {voltage}, {frequency}".format(power=power, voltage=voltage, frequency=frequency))

    time.sleep(APP_DELAY)


if __name__ == "__main__":

    radio.init()
    OpenThings.init(Devices.CRYPT_PID)

    try:
        while True:
            energy_monitor_loop()
    finally:
        radio.finished()

