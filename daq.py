class DAQ():
	"""Dies ist eine Klassenimplementierung einer DAQ Karte."""

	def __init__(self, device):
		"""Dies ist die init Methode einer Klasse, sie wird immer automatisch
		aufgerufen wenn ein Objekt der Klasse erzeugt wird."""
		self.port = serial.Serial(port=device, baudrate=115200, bytesize=8,
							parity='N', stopbits=1, timeout=0.5, xonxoff=True)
		time.sleep(0.5)
		self.write("ST 0", 0.1) #Minuetliche Status Updates ausschalten
		self.write("VE 0", 0.1) #Veto ausschalten

	def read(self):
		"""Diese Funktion liest den Output von der DAQ Karte ein."""
		output =  self.port.readline()
		return output[:-2]

	def write(self, message, wait=0):
		"""Diese Funktion schickt einen Befehl an die DAQ Karte."""
		self.port.write(str(message)+"\r")
		time.sleep(wait)

	def set_thresholds(self, t1=200, t2=200, t3=200):
		"""Diese Funktion setzt die Schwellenspannung fuer die drei Kanaele."""
		for channel, threshold in zip(range(3), [t1,t2,t3]):
			print "Schwelle fuer Kanal %s: %smV" % (channel, threshold)
			self.write("TL %s %s" % (channel, threshold))

	def set_trigger(self, trigger=3):
		if trigger == 3:
			self.write("WC 00 27")
			print "Dreifach-Trigger wird verwendet"
		elif trigger == 2:
			self.write("WC 00 1F")
			print "Zweifach-Trigger wird verwendet"
		else:
			print "Gueltige trigger sind 2 oder 3!"
			sys.exit(0)

	def measure(self, runtime):
		print "\nBeginne Messung ... (%ss Messzeit)" % runtime
		self.write("CD", 0.1)
		self.write("RB", 0.1) # Zaehler zuruecksetzen

		start, counter, t, cycle = 0, 0, 0, 0

		while t<runtime:
			self.write("DS")
			output =  self.read()
			while not (output.startswith("DS") and len(output) > 5):
				time.sleep(0.01)
				output = self.read()
			else:
				if output.startswith("DS") and len(output) > 5:
					outputlist = [int(f[3:],16) for f in output.split(" ") if len(f)>3]
					internal_count = outputlist[-1]
					if internal_count<counter:
						cycle +=1
					if start == 0:
						start = internal_count - 1
					counter = internal_count
					total_count = internal_count - start + cycle * 4294967296
					t = total_count * 0.000000040
		self.write("CE", 0.1)
		return t, outputlist
