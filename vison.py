import sys
from multiprocessing import Process
import subprocess
import time
import os
import json
	
try:
	TEAM_NUMBER = sys.argv[1]
	DARKNET_PATH = sys.argv[2].replace('\\','/')
	DARKNET_EXECUTABLE = DARKNET_PATH + "/" +sys.argv[3]
	DARKNET_ARGS = sys.argv[4:]
	
except:
	raise IndexError("bad args")
	
class Darknet(Process):
	def __init__(self, path, executable, args):
		Process.__init__(self,name='my_service')
		self.path = path
		self.executable = executable
		self.args = args
		self.addresses = {}
		self.isDarknetRunning = False
		self.darknetProc = None
		self.mw = None
		self.objects = {}
		
	def start_darknet(self):
		from memorpy import MemWorker
		self.addresses = {}
		print(self.executable)
		self.darknetProc = subprocess.Popen([self.executable] + self.args, stdout=subprocess.PIPE)
		time.sleep(5)
		self.mw = MemWorker(pid=int(self.darknetProc.pid))#name #pid
		self.load_addresses()
		self.isDarknetRunning = True
		
	def stop_darknet(self):
		self.isDarknetRunning = False
		self.addresses = {}
		self.darknetProc.kill()
		
	def get_darknet_output(self):
		return darknetProc.communicate()[0]
		
	def run(self):
		length = self.addresses['detectedObjectsLength'].read()
		self.objects = self.addresses['detectedObjects'](maxlen=length)
		time.sleep(0.01)
		
	def load_addresses(self):
		with open(self.executable+"-"+str(self.darknetProc.pid)+"-streamedFile.data", 'r') as f:
			self.addresses = json.load(f)		
		
		for key,val in self.addresses.items():
			self.addresses[key] = self.load_mem_addr(*self.addresses[key])
		
	def load_mem_addr(self, addr, type, length=1):
		from memorpy import Address
		addrInt = int(addr, 16)
		a = Address(addrInt,self.mw.process,type)
		return a
		
	def get_objects(self):
		return self.objects

def main():
	darknet = Darknet(DARKNET_PATH,DARKNET_EXECUTABLE,DARKNET_ARGS)
	os.chdir(DARKNET_PATH)
	darknet.start_darknet()
	darknet.start()
	while 1:
		print(darknet.get_objects())
		time.sleep(0.01)

if __name__ == "__main__":
	main()