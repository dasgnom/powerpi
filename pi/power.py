#!/usr/bin/env python3

from select import poll, POLLPRI, POLLIN, POLLERR
import sys
import os
import threading
import time
import queue
import requests
import configparser

def trans():
	global serverconf
	# build together url and headers
	uri = ""
	if serverconf.getboolean("ssl") == True:
		uri = "https://"
	else:
		uri = "http://"
	uri = uri + serverconf["url"] + "/get.php"
	if sys.stdout.isatty():
		print("Remote URI: " + uri)
	queuelast = time.time()
	while True:
		# get value from queue (blocking)
		queuedata = powerqueue.get()
		powerqueue.task_done()
		queuetime = int(queuedata[0])
		queueval = str(queuedata[1])
		# if more than five seconds passed since last event
		if ((queuetime - queuelast) >= 5):
			# put payload together
			payload =  {"val": str(queuetime) + ";" + str(queueval)}
			if sys.stdout.isatty():
				print("request " + uri + " => "+repr(payload))
			# send to webserver via http post
			#
			# Um den Krempel hier muss noch mal eine While Schleife rum, damit die Daten nicht verloren gehen.
			#
			try:
				if serverconf.getboolean("basicauth") == True:
					r = requests.post(uri, data=payload, verify=False, auth=(serverconf["user"], serverconf["password"]), timeout=10, headers={'connection':'close'})
				else:
					r = requests.post(uri, data=payload, verify=False, timeout=10, headers={'connection':'close'})
			except:
				print("Exception raised!")
			else:		
				if sys.stdout.isatty():
					print("server response: " + str(r.status_code))
			queuelast = queuetime
		
		else:
			# drop data if less than five seconds passed since last event
			del queuedata
			if sys.stdout.isatty():
				print("Drop queued element")

def readgpio():
	global gpiopath
	global gpioconf
	global smconf
	# open gpio filehandle
	gpio = open(gpiopath + "value", "r")
	# setup polling
	gpiopoll = poll()
	gpiopoll.register(gpio, POLLERR)
	
	# wait for two interrupts to have a "clean" starting point
	if sys.stdout.isatty():
		print("wait for 2 interrupts...")
	gpioevent = gpiopoll.poll()
	gpio.read()
	gpio.seek(0)
	if sys.stdout.isatty():
		print("wait for 1 interrupt....")
	gpioevent = gpiopoll.poll()
	last = time.time()
	gpio.read()
	gpio.seek(0)
	
	# start readgpio mainloop
	if sys.stdout.isatty():
		print("start readgpio mainloop")
	while True:
		gpioevent = gpiopoll.poll()
		gpioval = gpio.read(1)
		gpio.seek(0)
		# check if interrupt was a falling edge (yes, really!)
		if gpioval == '0':
			now = time.time()
			# plausibility check
			if ((now-last) >= gpioconf.getfloat("mintime")):
				# calculate current power consumption
				power = round((3600000/smconf.getint("impkwh")) / (now-last),2)
				if sys.stdout.isatty():
					print("Current power consumption: " + str(power) + " Watt")
					print("GPIO state: " + gpioval)
				# put measured value on queue
				powerqueue.put([now, power])
				last = now
		# error if a tty is connected and a raising edge was triggered
		else:
			if sys.stdout.isatty():
				print("ERROR: not a falling edge! Ignoring interrupt")


if __name__ == "__main__":
	# read config
	conf = configparser.ConfigParser()
	conf.read("powerpi.conf")
	conf.sections()
	gpioconf = conf['gpio']
	serverconf = conf['server']
	smconf = conf['smartmeter']
	if serverconf["url"] == "power.example.com":
		print("FATAL: configuration not adapted! Aborting!")
		exit(1)
	gpiopath = "/sys/class/gpio/gpio" + gpioconf["port"] + "/"
	# initialise gpio interfaces
	try:
		if not os.path.exists(gpiopath):
			# if not already exported, export gpio port
			gpioinit = open("/sys/class/gpio/export", "w") 
			gpioinit.write(gpioconf["port"] + "\n")
			gpioinit.close()
		# set direction of gpio port to "IN"
		gpiopin = open(gpiopath + "direction", "w")
		gpiopin.write("in")
		gpiopin.close()
		# set trigger to falling edge
		gpiotype = open(gpiopath + "edge", "w")
		gpiotype.write("falling")
		gpiotype.close()
	except:
		# if not able to initialise gpios: abort with error
		sys.stderr.write("can't initialize gpio interface\n")
		sys.stderr.flush()
		sys.exit(1)
	# defining queue for measured values
	powerqueue = queue.Queue()

	# disable ssl "no verification" warnings
	if serverconf.getboolean("sslself") == True:
		requests.packages.urllib3.disable_warnings()
	
	# initialising and starting threads
	th1 = threading.Thread(target=readgpio)
	th2 = threading.Thread(target=trans)
	th1.setDaemon(True)
	th2.setDaemon(True)
	th1.start()
	th2.start()
	
	#busy loop
	while True:
		time.sleep(1)
