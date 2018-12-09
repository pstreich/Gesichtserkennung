#Bibliotheken einbinden
import RPi.GPIO as GPIO
import sys
import time
import datetime
import numpy as np
import gspread
import oauth2client.client 
import json	# zum Einlesen der Google Zugangsdaten aus entsprechender Datei
import cPickle


#json Dateiname fuer Google Zugangsdaten
JSON_FILENAME       = 'pitest-c7f0752a993d.json'

# Google Dokumentname
GSHEET_NAME = 'pi'

# laedt Zugangsdaten aus json Datei und oeffnet Dokument zum schreiben
json_key = json.load(open(JSON_FILENAME))
creds = oauth2client.client.SignedJwtAssertionCredentials(json_key['client_email'], 
		json_key['private_key'],
		['https://spreadsheets.google.com/feeds'])
client_inst = gspread.authorize(creds)
gsheet = client_inst.open(GSHEET_NAME).sheet1



#GPIO Modus 
GPIO.setmode(GPIO.BCM)

#GPIO Pins zuweisen
GPIO_TRIGGER = 6
GPIO_ECHO = 12

#Richtung der GPIO-Pins festlegen (Eingabe/Asugabe)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
liste = np.zeros(60)
i = 0

def distanz():
	# setze Trigger auf HIGH
	GPIO.output(GPIO_TRIGGER, True)

	# setze Trigger nach 0.01ms auf LOW
	time.sleep(0.00001)
	GPIO.output(GPIO_TRIGGER, False)

	StartZeit = time.time()
	StopZeit = time.time()

	# speichere Startzeit
	while GPIO.input(GPIO_ECHO) == 0:
		StartZeit = time.time()

	# speichere Ankunftszeit
	while GPIO.input(GPIO_ECHO) == 1:
		StopZeit = time.time()

	# Zeit Differenz zwischen Start und Ankunft
	TimeElapsed = StopZeit - StartZeit
	# mit der Schallgeschwindigkeit (34300 cm/s) multiplizieren
	# und durch 2 teilen, da hin und zurueck
	distanz = (TimeElapsed * 34300) / 2

	return distanz


try:

	while True:
		# Misst Abstand und legt Liste/Array an zur Durchschnittsberechnung
		abstand = distanz()
		print ("Gemessene Entfernung = %.1f cm" % abstand)
		liste[i]=abstand
		i+=1
		time.sleep(1)

		# Nach ungefeahr 60 Sekunde
		if i == 55:
			# oeffnet Pickle Datei und liest Positionswert des Betrachters aus
			fp = open("shared.pk1", "rb")
			shared = cPickle.load(fp)
			# berechnet Distanzdurschnitt
			durschnitt = liste.mean()
			print str(durschnitt)
			print shared["xs"]
			print shared["ys"]
			curr_time = datetime.datetime.now()

			# Schreibt neue Zeile ins Google Dokument mit Datum, Distanz und X und Y Position
			gsheet.append_row((curr_time, str(int(durschnitt))+" cm", shared["xs"], shared["ys"]))

			# Setzt Liste mit Distanzwerten zurueck 
			i=0

	# Beim Abbruch durch STRG+C beenden
except KeyboardInterrupt:
	GPIO.cleanup()
	sys.exit(0)