#!/usr/bin/env python

import time
import requests
import signal
import sys
import threading
import random
import logging

#initialise some startup values
last = time.time()
current = time.time()
lpower = 10000
power = 0
thGpioExit = False
thTranExit = False
debug = False
server = "https://strom.ccc-ffm.de"
doMeasurement = None
doTransfer = None
simulation = False

def measure():
	GPIO.wait_for_edge(24, GPIO.FALLING)

def simulate(data=None):
	if data == None:
		time.sleep(random.randrange(1, 20, 1)/10)
	else:
		time.sleep(1)
		
def transSimulate(data=None):
		time.sleep(random.randrange(1, 20, 1)/10)
		return("HTTP 1.0 - 200")

def transfer(data):
	r = requests.post(server, data=data, verify=False)
	if debug:
		return(r)

#define function trapping the gpio interrupts
def trapGpio():
	global last
	global current
	global power
	while True:
		#wait for a falling edge on gpio 24
		doMeasurement()
		
		#get current time and calculate current power from difference
		current = time.time()
		diff = current - last
		power = 1800 / diff
		if debug:
			logging.debug("current power: " + str(power))
		if thGpioExit:
			break
		last = current
			
# define function transfering the measurments to our webserver
def powerTran(once=False):
	while True:
		if not once:
			time.sleep(5)
		out = str(int(current)) + ";" + str(round(power,0))
		payload = {"val": out}
		logging.debug("request: " + server + " => "+ out)
		transStatus = doTransfer(payload)
		if simulation:
			logging.debug("result: HTTP1.0:200")
		else:
			logging.debug(transStatus)
		if once:
			break
		if thTranExit:
			break

def sigtermHandler(signal, stack):
	if signal == 2:
		signal = "SIGINT"
	elif signal == 15:
		signal = "SIGTERM"

	logging.info("Signal '%s' received", signal)
	logging.info("--- powerpi schutdown invoked ---")
	global th1, th2, thTranExit, thGpioExit
	thGpioExit = True
	th1.join()
	thTranExit = True
	if not simulation:		
		GPIO.cleanup()
	logging.info("--- powerpi shutdown completed ---")
	sys.exit(0)



def initPowerPi():
	global last, debug, doMeasurement, doTransfer, simulation

	#checking for debugging mode flag
	if "-d" in sys.argv:
		debug=True
		logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s - %(levelname)8s - %(message)s')
	else:
		logging.basicConfig(filename = '/var/log/powerpi.log', level = logging.INFO, format = '%(asctime)s - %(levelname)8s - %(message)s')
		
	logging.info("--- starting powerpi ---")
	
	#checking for simulation mode flag
	if "-s" in sys.argv:
		logging.info("But it's just a SIMULATION!")
		simulation = True
		doMeasurement = simulate
		doTransfer = simulate
	else:
		doMeasurement = measure
		doTransfer = transfer
		try:
			import RPi.GPIO as GPIO
		except:
			logging.critical("Module GPIO not found ... Abort!")
			sys.exit(1)
			
		# set gpio port numeration to bcm style
		GPIO.setmode(GPIO.BCM)
		
		#initialise gpio on pi 24 as input with an pull_up resistor
		GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	
	#wait for two interrupts to obtain "clean" data
	for i in range(2):
		doMeasurement()	
		logging.debug("waiting for 2 interrupts ...   [ %s seen ] " % (i))
	logging.debug("waiting for 2 interrupts ...   [ %s seen ] " % (2))

	last = time.time()

	global th1, th2
	
	#initialise threads waiting fpr gpio interrupts and tansfering power data
	logging.debug("starting thread trapGpio")
	th1=threading.Thread(target=trapGpio)
	logging.debug("starting thread powerTran")
	th2=threading.Thread(target=powerTran)
	
	#daemonize these threads
	th1.setDaemon(True)
	th2.setDaemon(True)

	#start these threads
	th1.start()
	th2.start()	
	
	logging.info("start up completed - entering logging mode")
	
	
if __name__ == "__main__":

	# setting up signal trapping for SIGINT and SIGTERM
	signal.signal(signal.SIGTERM, sigtermHandler)
	signal.signal(signal.SIGINT, sigtermHandler)
	
	# call initialising function
	initPowerPi()

	# busyloop
	while True:
		raw_input("")
