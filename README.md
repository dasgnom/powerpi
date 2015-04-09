# POWERPI
Logs the electric energy consumption in the hq with the power of a raspberry and a flying circus.

## Voraussetzungen

### Hardware
  * Raspberry Pi B2
  * Stromzähler mit S0-Schnittstelle
  * $Server
 
### Software

#### RaspberryPi
  * Raspbian 7.8
  * python 3.2
    * requests >= 2.5

#### Server
  * Apache >= 2.2
  * php5 >= 5.0
  * rrdtool >= 1.4
  * cron
  
## Bestandteile
Das Setup besteht aus zwei Bestandteilen. Der eine läuft auf einem RasPi der im Sicherungskasten im HQ hängt und die Impulse vom Stromzähler abgreift. Der Andere Teil läuft auf unserem Server, auf der VM mtbf. Dieser Teil nimmt die Rohdaten vom RasPi entgegen, schreibt sie in eine RRD und erzeugt einmal in der Minute hypsche Bilder daraus.

## Installation

### Raspberry Pi
Inhalt des Unterordners *pi* auf einen RasPi kopieren, auf dem ein Raspbian läuft. Das Script *power.py* muss in den Ordner /srv/powerpi und das Script *powerpi* in den Ordner /etc/init.d/ kopieren.
Das Script `/srv/powerpi/power.py` muss für root ausführbar sein.

#### AutoStart 

Damit der Daemon automatisch gestartet wird muss der Befehl `insserv -d /etc/init.d/powerpi` als root ausgeführt werden.

### Server
Auf dem Webserver muss das Script *get.php* erreichbar sein. 