#!/usr/bin/env python
"""Diese Datei zeigt wie man mit der DAQ-Karte Messungen durchfuehrt.
   Inspired by muonic  http://code.google.com/p/muonic/
   DAQ Card Manual: http://physik-begreifen-zeuthen.desy.de/sites2009/site_PhyBegZ/content/e2198/e2451/e6374/e129804/e129813/infoboxContent129819/DAQ-KarteUserManual_ger.pdf
   2014 Dominik Haitz <dhaitz@cern.ch>
"""

import serial
import time, sys, math, argparse
import matplotlib.pyplot as plt
from daq import DAQ

def argumente():
	"""Diese Funktion liest Argumente von der Kommandozeile ein."""
	parser = argparse.ArgumentParser()

	parser.add_argument('-d', '--device', type=str, default="/dev/ttyUSB0",
	help="Der Name der Schnittstelle die angesprochen werden soll. Default ist %(default)s")
	parser.add_argument('-T', '--trigger', type=int, default="3",
	help="Der Trigger der verwendet werden soll. Default ist %(default)s")
	parser.add_argument('-t', '--time', type=int, default="10",
	help="Laufzeit fuer eine Messung. Default ist %(default)s")

	parser.add_argument('-s', '--schwellen', type=int, nargs="*", default=[100, 100, 100],
	help="Schwellenspannungen (in mV) fuer die drei Kanaele. Default ist %(default)s")

	parser.add_argument('-g', '--graphical', action="store_true",
	help="Erzeuge eine grafische Darstellung von Messreihen. Wenn diese Option \
			nicht gesetzt ist wird einfach das Ergebnis einer Messung im Terminal ausgegeben.")

	return parser.parse_args()


if __name__ == '__main__':
	"""Dies ist die main Methode des Skripts, d.h. diese wird ausgefuehrt wenn
	man das Skript direkt mit `python muonrate.py` startet."""

	opt = argumente()

	# Hier erzeugen wir ein Objekt namens daqcard vom Typ DAQ
	daqcard = DAQ(opt.device)

	# Schwellenspannungen und Trigger setzen
	daqcard.set_thresholds(*opt.schwellen)
	daqcard.set_trigger(opt.trigger)

	if not opt.graphical:
		# Messung starten
		t, outputlist = daqcard.measure(opt.time)

		# Ergebnisse ausgeben
		print "\nErgebnis nach %.2f Sekunden Messzeit:" % t
		for i in range(3):
			print "Kanal %s: %.0f Ereignisse" % (i+1, outputlist[i])
		print "Trigger:   %.0f Ereignisse" % outputlist[4], "  Stat. Fehler: %.0f Ereignisse" % math.sqrt(outputlist[4])
		print "\nTriggerrate: %.2f +- %.2f  Hz" % ((outputlist[4]/t), (math.sqrt(outputlist[4])/t))

	else:
		fig=plt.figure()
		plt.ion()
		plt.show()
		plt.xlabel("Messung")
		plt.ylabel("Triggerrate / Hz")

		x, y, yerr = [], [], []
		i = 0

		while True:
			i += 1
			t, outputlist = daqcard.measure(opt.time)

			x.append(i)
			y.append((outputlist[4]/t))
			yerr.append(math.sqrt(outputlist[4])/t)

			plt.axis([0,i+1,0,max(y)*1.2])
			plt.errorbar(x, y , yerr)
			plt.draw()

