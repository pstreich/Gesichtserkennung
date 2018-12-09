# Bibliotheken einbinden
import numpy as np
import cv2

def resize(image, width = None, height = None, inter = cv2.INTER_AREA):
	# Initialisiert Dimensionen des zu skalierenden Bildes und greift auf Bildgroesse zu
	dim = None
	(h, w) = image.shape[:2]

	# wenn breite und laenge nicht vorhanden, gib Original wieder
	if width is None and height is None:
		return image

	# ueberpruft ob breite vorhanden
	if width is None:
		# berechnet Laengenverhaeltnis und konstruiert Dimensionen
		r = height / float(h)
		dim = (int(w * r), height)

	# wenn nicht, keine Groesse vorhanden
	else:
		# berechnet Breitenverhaeltnis und konstruiert Dimensionen
		r = width / float(w)
		dim = (width, int(h * r))

	# skaliert Bild
	resized = cv2.resize(image, dim, interpolation = inter)

	# gibt skaliertes bild zurueck
	return resized