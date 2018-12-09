# USAGE test
# python webcam_servo.py --face cascades/haarcascade_frontalface_default.xml

# Einindung Bibliotheken
from ausgelagert.face import Gesichtserkenner
from ausgelagert import servo
from ausgelagert import skalierung
from picamera.array import PiRGBArray
from picamera import PiCamera
import cPickle 	# zum Zwischenspeichern von Daten, hier fuer Positionsdaten
import argparse # zur Uebermittlung von Argumenten fuer Kommandozeilebefehle
import time
import datetime
import cv2	# OpenCV
import os
import sys
import RPi.GPIO as GPIO


# Definiert Variablen fuer Position zum Senden an Pickle Datei/Google
xserv = "nicht vorhanden"
yserv = "nicht vorhanden"	
xserv_rechts = 0
xserv_links = 0	
yserv_unten = 0
yserv_oben = 0


# Definiert Pin Nummer fuer Bewegungsmelder
sensor = 5

# Definiert GPIO Modus, da Sensor, Eingabemodus
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor, GPIO.IN, GPIO.PUD_DOWN)

# Zum kontrollieren des Zustands des Bewegungsmelders
previous_state = False
current_state = False

# Konstruiert argument parse und parst Argumente
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--face", required = True,
	help = "path to where the face cascade resides")
ap.add_argument("-v", "--video",
	help = "path to the (optional) video file")
args = vars(ap.parse_args())

# Initialisiert Kamera und Referenz zu Rohaufzeichnung
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))


# Servomotoren
XSchritt = 2 # Aenderungsgrad fuer x Achse
YSchritt = -2 # Aenderungsgrad fuer y Achse
servoXPosition = 110 # initiale x Achse
servoYPosition = 115 # initiale y Achse
XGpioPin = 1  # servoblaster pin 1 : gpio pin 17 
YGpioPin = 2  # servoblaster pin 2 : gpio pin 18

# Konstruiert Gesichtserkenner und waermt Kamera vor
fd = Gesichtserkenner(args["face"])
time.sleep(0.1)

try:
	while True:
		# Speichert Startzeit
		start_time = time.time()
		# Ermittel Bewegungsmelder Zustand 
		previous_state = current_state
		current_state = GPIO.input(sensor)
		if current_state != previous_state:
			new_state = "HIGH" if current_state else "LOW"
			print ("GPIO pin %s is %s" % (sensor, new_state))

			if current_state:
				# Einfangen von Frames aus Kameraaufzeichnung
				for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
					# Greift auf NumPy Array zu der Frames represaentiert
					frame = f.array

					# Skaliert Bild und konvertiert in Graustufen
					frame = skalierung.resize(frame, width = 300)
					gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

					# Findet Gesicht und klont Frame
					# um Rechteck darauf zu zeichnen
					faceRects = fd.detect(gray, scaleFactor = 1.1, minNeighbors = 5,
						minSize = (30, 30))
					frameClone = frame.copy()

					# geht Rechtecke durch und zeichnet diese
					for (fX, fY, fW, fH) in faceRects:
						cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH), (0, 255, 0), 2)
						if fX<60:
							print("links")
							xserv_links+= 1
						elif fX>170: 
							print("rechts")
							xserv_rechts+= 1
						if fY<60:
							print("oben")
							yserv_oben+= 1
						elif fY>120 : 
							print("unten")
							yserv_unten+= 1

						# Bewegt Servomotoren
						servo.move(XGpioPin, servoXPosition)
        					servo.move(YGpioPin, servoYPosition)

						# Wenn Gesicht zu weit links
                				if(fX<100):
                    				# Bewege Servo nach rechts
                    					servoXPosition += XSchritt
                				# Wenn Gesicht zu weit rechts
                				elif(fX>170):
                    				# Bewege Servo nach links
                    					servoXPosition -= XSchritt
 
                				# Bewegt Servomotoren
                				servoXPosition = min(servoXPosition, servo.max_pwm)
                				servoXPosition = max(servoXPosition, servo.min_pwm)               
                				servo.move(XGpioPin, servoXPosition)

                				#Wenn Gesicht zu weit oben
                				if(fY < 100):
                    					if(servoYPosition <= servo.max_pwm):
                        				#Bewege Servo nach unten
                        					servoYPosition += YSchritt
                				#Wenn Gesicht zu weit unten
                				elif(fY>120):
                    					if(servoYPosition >= 1):
                        				#Bewege Servo nach oben
                        					servoYPosition -= YSchritt
 						
 						# Bewegt Servomotoren               
                				servoYPosition = min(servoYPosition, servo.max_pwm)
                				servoYPosition = max(servoYPosition, servo.min_pwm)  
                				servo.move(YGpioPin, servoYPosition)



					# Zeigt gefundene Gesichter und loescht Frame
					cv2.imshow("Face", frameClone)
					rawCapture.truncate(0)

					# erneute Ermittlung von Bewegungsmelder Zustand
					current_state = GPIO.input(sensor)

					# Zeitmessung
					elapsed_time=time.time()-start_time
					if elapsed_time > 30:	
		


						# Abfrage/Festlegung der Positionsdaten
						if xserv_rechts and xserv_links == 0 : xserv = "nicht vorhanden"
						elif (xserv_rechts > 0) == (xserv_links > 0) : xserv = "mittig"
						elif xserv_rechts > xserv_links : xserv = "rechts"
						else : xserv = "links"
						if yserv_oben and yserv_unten == 0 : yserv = "nicht vorhanden"
						elif (yserv_oben > 0) == (yserv_unten > 0) : yserv = "mittig"
						elif yserv_oben > yserv_unten : yserv = "oben"
						else : yserv = "unten"

						# Erstellung einer pickle Datei zur Zwischenspeicherung der Positionsdaten
						fp = open("shared.pk1","wb")
						# Daten werden in pickle Datei geschrieben
						shared = {"xs":xserv, "ys":yserv} 
						cPickle.dump(shared,fp)
						
						# Abfrage des Bewgegungsmelder Zustand
						if elapsed_time > 55:
							if not current_state:
							#Falls keine Bewegung vorhanden
								# Ueberpruefe ob kein Gesicht vorhanden
								if len(faceRects) == 0:
								# Falls kein Gesicht gefunden, dann verlasse Schleife und setze Zeitmessung zurueck
									# Setzt Positionsdaten zurueck
									xserv_rechts = 0
									xserv_links = 0
									yserv_oben = 0
									yserv_unten = 0
									start_time = time.time()	
									break;

					

					# Bei Betaetigung von 'q' verlasse Schleife 
					if cv2.waitKey(1) & 0xFF == ord("q"):
						GPIO.cleanup()
						sys.exit(0)

#und beende Prozess
except KeyboardInterrupt:
	sys.exit(0)

