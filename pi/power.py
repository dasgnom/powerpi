#!/usr/bin/env python3

from select import poll, POLLPRI, POLLIN, POLLERR
import sys
import os
import threading
import time
import queue
import requests
import configparser
import logging

def trans():
	global serverconf
	# build together url and headers
	uri = ""
	if serverconf.getboolean("ssl") == True:
		uri = "https://"
	else:
		uri = "http://"
	uri = uri + serverconf["url"] + "/get.php"
	log.info('Remote URI: {}'.format(uri))
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
			log.debug('request {} => {}'.format(uri, repr(payload)))
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
				log.error('server response: {}'.format(str(r.status_code)))
			queuelast = queuetime
		
		else:
			# drop data if less than five seconds passed since last event
			del queuedata
			log.info('dropped queued element')

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
	log.info('waiting for 2 interrupts to get a clean start')
	gpioevent = gpiopoll.poll()
	gpio.read()
	gpio.seek(0)
	log.info('waiting for 1 interrupt to get a clean start...')
	gpioevent = gpiopoll.poll()
	last = time.time()
	gpio.read()
	gpio.seek(0)
	
	# start readgpio mainloop
	log.info('start readgpio mainloop')
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
				log.info('Current power consumption: {} Watt'.format(str(power)))
				log.debug('GPIO state: {}'.format(gpioval))
				# put measured value on queue
				powerqueue.put([now, power])
				last = now
		# error if a tty is connected and a raising edge was triggered
		else:
			log.debug('Not a falling edge, ignoring')


if __name__ == "__main__":
	# read config
	conf = configparser.ConfigParser()
	conf.read("powerpi.conf")
	conf.sections()
	gpioconf = conf['gpio']
	serverconf = conf['server']
	smconf = conf['smartmeter']
	# configure logging
	log = logging.getLogger(__name__)
	if serverconf["url"] == "power.example.com":
		log.critical('Server -> url still default value')
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
		log.critical('can not initialize gpio interface. aborting.')
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
