//Einbindung der Bibliotheken
// Arduino und serielle Kommunikation
import cc.arduino.*;
import processing.serial.*;
// OpenCV, video processing, Java 
import gab.opencv.*;
import processing.video.*;
import java.awt.*;
import java.awt.Toolkit;


// Klasse fuer Servomotoren
class Servo {
int pin, position = 0, min = 0, max = 90;
Servo(int p, int mi, int ma) {
pin = p;
min = mi;
max = ma;
}

// Funktion fuer Servobewegung
void move(float increment) {
if (position + increment >= min && position + increment <= max) {
position += increment;
arduino.servoWrite(pin, position);
delay(10);
}
}

// Funktion um Senden der Servobewegung an die Firmata
void move() {
arduino.servoWrite(pin, position);
}
}



Capture cam;                  									// Kamera Variable
OpenCV opencv;                  								// OpenCV Variable
Arduino arduino;                								// Arduino Objekt Variable
int servoXpin = 3, servoYpin = 2;        						// GPIO Nummern für Servomotoren
Servo servoX = new Servo(servoXpin, 0, 180);  					// x Motor Objekt GPIO, Limitierungen
Servo servoY = new Servo(servoYpin, 0, 120);  					// y Motor      "    "
Rectangle gesicht = null, gesichtziel = null;   				// Gesichterumrahmung Rechtecke


boolean gefunden = false;            							// Wenn Gesicht gefunden, true
boolean mittig = false;            								// Wenn Gesicht mittig, true
PVector increment = new PVector(1, 10);
boolean erster = true;     										// Jeweils Erster Durchlauf
int[] delay = {0, 0};


void setup() {
size(800, 600);                  								// Setzt Fenstergroesse 
frameRate(30);
cam = new Capture(this, 160, 120);        						// Definiert Aufzeichnung mit gesetzter Fenstergroesse
opencv = new OpenCV(this, cam);          						// Definiert OpenCV Objekt mit gesetzter Fenstergroesse

opencv.loadCascade(OpenCV.CASCADE_FRONTALFACE);  				// laedt OpenCV Gesichtserkennung Cascade Datei
cam.start();//begin capturing camera images

arduino = new Arduino(this, Arduino.list()[0], 57600);    		// Initialisiert Kommunikation mit Arduino (Objekt, Schnitsttelle, Rate)

arduino.pinMode(servoXpin, Arduino.SERVO);    					// Setzt Pin fuer X Servo
arduino.pinMode(servoYpin, Arduino.SERVO);    					// Setzt Pin fuer Y Servo
strokeWeight(0.5);                								// Setzt Strichgroesse
initialisiere();
}

void draw() {
opencv.loadImage(cam);              							// laedt Bild in OpenCV 
Rectangle[] gesichter = opencv.detect();      					// Ueberpruft ob Gesicht im Bild

scale(5);                    									// Skaliere angezeigtes Bild um 5

rect(0, cam.height, cam.width, 80);    image(cam, 0, 0);    	// Zeichnet Aufzeichnung
scale(1);                    									// Setzt Skalierung zurueck

switch(gesichter.length) {              						// Anhand Anzahl gefundener Gesichter fuerhst folgenden Aktionen aus
case 0 :                    									// 0
nicht_vorhanden();
break;                      
case 1 :                    									// 1
vorhanden(gesichter[0]);              							// Fuege Gesicht in 1(0) Position des Arrays
break;
default :                  
break;              
}

if (gesicht != null) {
mittig = true;                          						// Standardwert
if (gesicht.x + (gesicht.width/2) > cam.width/2 ) {  			// wenn Gesicht mehr als 5Pixel links von Mitte
mittig = false;                          
if (gefunden) {
println("rechts");
servoX.move(-1);                          						// Bewegt X Servo
}
}
if (gesicht.x + (gesicht.width/2) < cam.width/2) {  			// wenn Gesicht mehr als 5Pixel rechts von Mitte
mittig = false;                          
if (gefunden) {
println("links");
servoX.move(1);                            						// Bewegt X Servo
}
}
if (gesicht.y + (gesicht.height/2) > cam.height/2) {  			// wenn Gesicht mehr als 5Pixel unter Mitte
mittig = false;                          
if (gefunden) {
println("unten");
servoY.move(1);                            						// Bewegt Y Servo
}
}
if (gesicht.y + (gesicht.height/2) < cam.height/2) {  			// wenn Gesicht mehr als 5Pixel ueber Mitte
mittig = false;                          
if (gefunden) {
println("oben");
servoY.move(-1);                          						// Bewegt Y Servo
}
}
}
}

void initialisiere() {                          
anfang();
}

void captureEvent(Capture c) {                    				// Benoetige Aktion zum Einlesen von Kamera
c.read();
}

void nicht_vorhanden() {
gefunden = false;
}

void vorhanden(Rectangle newFace) {
gefunden = true;
erster = true;                        											// Servomotoren werden zum Ausgangspunkt bewegt wenn laengere Zeit kein Gesicht gefunden wird
gesichtvar(newFace);            												// Gefundenes Gesicht in Variable schreiben
displayCrosshairs();                        									// Zeigt Rechteck über Ziel und aktuelle Position an
}

void gesichtvar(Rectangle incoming) {              								// Population von Ziel und Gesicht Variablen
gesicht = incoming;                          									// Setzt Variable auf neues Gesicht
gesichtziel = new Rectangle(cam.width/2 - gesicht.width/2, cam.height/2 - gesicht.height/2, gesicht.width, gesicht.height);  // Setzt Zielrahmen 
}

void displayCrosshairs() {
fill(0, 255, 0, 0);                        										// Setzt Fuellfarbe unsichtbar
stroke(0, 255, 0);                          									// Setzt Rahmenfarbe gruen
rect(gesichtziel.x, gesichtziel.y, gesichtziel.width, gesichtziel.height);     	// Zeigt Gesichtsrahmen an
}

void anfang() { 																// Ausgangszustand
if(erster){
servoX.position = 90;
servoY.position = 90;
servoX.move();
servoY.move();
}
erster = false;
}