#!/usr/bin/python

import RPi.GPIO as GPIO
import time

# set gpio port numeration to bcm style
GPIO.setmode(GPIO.BCM)

#initialise gpio on pi 24 as input with an pull_up resistor
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#initialise some startup values
last = time.time()
lpower = 10000

#start busy loop
while True:
	#wait for a falling edge on gpio 24
	GPIO.wait_for_edge(24, GPIO.FALLING)
	
	#get current time and calculate current power from difference
	current = time.time()
	diff = current - last
	power = 1800 / diff

	#write into logfile
	logfile = open("/srv/powerpi/power.out", "w+", 0)
	if (power < lpower + 1500):
		out = str(current) + ";" + str(round(power,0))	
	else:
		out = str(current) + ";0"
	logfile.write(out)
	logfile.close()
	lpower = power
	last = current
GPIO.cleanup()
