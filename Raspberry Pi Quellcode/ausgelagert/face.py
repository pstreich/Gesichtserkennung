# Bibliotheken einbinden
import cv2

class Gesichtserkenner:
	def __init__(self, faceCascadePath):
		# laedt Gesichtserkenner
		self.faceCascade = cv2.CascadeClassifier(faceCascadePath)

	def detect(self, image, scaleFactor = 1.1, minNeighbors = 5, minSize = (30, 30)):
		# erkennt Gesichter in Bilder
		rects = self.faceCascade.detectMultiScale(image,
			scaleFactor = scaleFactor, minNeighbors = minNeighbors,
			minSize = minSize, flags = cv2.CASCADE_SCALE_IMAGE)

		# Gibt Rechtecke die Gesichter umrahmen wieder
		return rects