import sys
from threading import Thread
import subprocess
import time
import os
import json
from libs.pymem import Pymem
from networktables import NetworkTables


LOCAL_PATH = os.getcwd()

try:
	TEAM_NUMBER = sys.argv[1]
	DARKNET_PATH = os.path.join(LOCAL_PATH, sys.argv[2])
	DARKNET_EXECUTABLE = os.path.join(DARKNET_PATH, sys.argv[3])
	DARKNET_ARGS = sys.argv[4:]
except:
	raise IndexError("bad args")
	
ROBOT_IP_ADDRESS = "roborio-{}-frc.local".format(TEAM_NUMBER)

class Darknet(Thread):
	def __init__(self, path, executable, args):
		Thread.__init__(self)
		self.path = path
		self.executable = executable
		self.args = args
		self.addresses = {}
		self.isDarknetRunning = False
		self.darknetProc = None
		self.mw = Pymem()
		self.objects = b'{}'
		
	def start_darknet(self):
		self.addresses = {}
		os.chdir(DARKNET_PATH)
		self.darknetProc = subprocess.Popen([self.executable] + self.args, stdout=subprocess.PIPE)
		while 1:
			try:
				self.mw.open_process_from_id(int(self.darknetProc.pid))
				break
			except (pymem.exception.CouldNotOpenProcess, TypeError):
				time.sleep(0.5)
		
		self.load_addresses()
		os.chdir(LOCAL_PATH)
		self.isDarknetRunning = True
		
	def stop_darknet(self):
		self.isDarknetRunning = False
		self.addresses = {}
		self.darknetProc.kill()
		
	def get_darknet_output(self):
		return darknetProc.communicate()[0]
		
	def run(self):
		try:
			while self.isDarknetRunning:
				length = self.mw.read_uint(int(self.addresses['detectedObjectsLength'][0], 0))
				pointer = self.mw.read_string(int(self.addresses['detectedObjects'][0],0),8)
				try: #sometimes memory reads error here
					self.objects = self.mw.read_string(int.from_bytes(pointer,'little'),length)
				except:
					pass
				time.sleep(0.01)
		except:
			print("Darknet has stopped running!")
			self.isDarknetRunning = False
			self.addresses = {}

	def load_addresses(self):
		os.chdir(DARKNET_PATH)
		fName = self.executable+"-"+str(self.darknetProc.pid)+"-streamedFile.data"
		while not os.path.exists(fName):
			time.sleep(0.5)
		if os.path.isfile(fName): 
			with open(fName, 'r') as f:
				self.addresses = json.load(f)	
			os.remove(fName)
			
		os.chdir(LOCAL_PATH)
		
	def get_objects(self):
		#print(self.objects.decode())
		return json.loads(self.objects.decode())

def main():
	NetworkTables.initialize(server=ROBOT_IP_ADDRESS)
	darknetNT = NetworkTables.getTable("DarknetVision")
	
	darknet = Darknet(DARKNET_PATH,DARKNET_EXECUTABLE,DARKNET_ARGS)
	darknet.start_darknet()
	darknet.start()
	while darknet.isDarknetRunning:
		a = darknet.get_objects()
		print(a)
		darknetNT.putString('runtimeData', a)
		time.sleep(0.01)
		
	print('Either something went wrong or the program ended successfully!')

if __name__ == "__main__":
	main()