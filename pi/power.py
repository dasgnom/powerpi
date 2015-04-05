#!/usr/bin/env python3

from select import poll, POLLPRI, POLLIN, POLLERR
import sys
import os
import threading
import time
import queue
import requests


def trans():
	queuelast = time.time()
	while True:
		queuedata = powerqueue.get()
		queuetime = int(queuedata[0])
		queueval = str(queuedata[1])
		if ((queuetime - queuelast) >= 5):
			payload =  {"val": str(queuetime) + ";" + str(queueval)}
			if sys.stdout.isatty():
				print("request https://strom.ccc-ffm.de:2342/get.php => "+repr(payload))
			r = requests.post("https://strom.ccc-ffm.de:2342/get.php", data=payload, verify=False, auth=('CCC', 'Freundschaft'))
			if sys.stdout.isatty():
				print(r)
			queuelast = queuetime
			

def readgpio():
	gpio = open("/sys/class/gpio/gpio24/value", "r")
	gpiopoll = poll()
	gpiopoll.register(gpio, POLLERR)
	if sys.stdout.isatty():
		print("wait for 2 interrupts...")
	gpioevent = gpiopoll.poll()
	gpio.read()
	gpio.seek(0)
	last = time.time()
	gpioevent = gpiopoll.poll()
	gpio.read()
	gpio.seek(0)
	if sys.stdout.isatty():
		print("start readgpio mainloop")
	while True:
		gpioevent = gpiopoll.poll()
		gpio.read()
		gpio.seek(0)
		now = time.time()
		power = round(1800 / (now-last),2)
		if sys.stdout.isatty():
			print("Current power consumption: " + str(power) + " Watt")
		powerqueue.put([now, power])
		last = now

if __name__ == "__main__":
	try:
		if not os.path.exists("/sys/class/gpio/gpio24"):
			gpioinit = open("/sys/class/gpio/export", "w") 
			gpioinit.write("24\n")
			gpioinit.close()
		gpiopin = open("/sys/class/gpio/gpio24/direction", "w")
		gpiopin.write("in")
		gpiopin.close()
		gpiotype = open("/sys/class/gpio/gpio24/edge", "w")
		gpiotype.write("falling")
		gpiotype.close()
	except:
		sys.stderr.write("can't initialize gpio interface\n")
		sys.stderr.flush()
		sys.exit(1)

	powerqueue = queue.Queue()
	
	th1 = threading.Thread(target=readgpio)
	th2 = threading.Thread(target=trans)
	th1.setDaemon(True)
	th2.setDaemon(True)
	th1.start()
	th2.start()
	
	while True:
		time.sleep(1)
