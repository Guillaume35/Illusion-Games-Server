import socket, threading, re
import igsconfig, path, regmods

# initializing
REGISTERED_MODS = regmods.get() # Registered modules
CLIENTS = {} # connected clients

for mod in REGISTERED_MODS:
	__import__('igsmods.'+mod)

class Client(threading.Thread):
	"""Accept and manage connection with a new client"""
	
	def __init__(self, client):
		threading.Thread.__init__(self)
		self.client = client
	
	def run(self):
		# Dialog with the client
		
		global CLIENTS
		
		client_name = self.getName()
		
		while True:
			q = self.client.recv(1024)
			
			if not q:
				break
			
			# Remove b'' used to encode message
			# TODO : Maybe there is a better way ?
			qstr = str(q)
			qstr = re.sub(r"^b'", "", qstr)
			qstr = re.sub(r"'$", "", qstr)
			qstr = re.sub(r'^b"', '', qstr)
			qstr = re.sub(r'"$', '', qstr)
		
			if re.search(r"^igs\.", qstr):
				# IGS registered modules
				qstr = re.sub(r"^igs\.", r"igsmods.", qstr)
			
				mod = re.sub(r"^igsmods\.(\w+)\.\w+\(.*\)\s*", r"\1", qstr)
			
				if mod in REGISTERED_MODS:
					try:
						r = eval(qstr)
					except:
						r = 'ER: There where a problem in your command execution. Check the syntax'
			
				else:
					r = 'ER: Module %s could not be found in IGS registered modules list' % mod
		
			else:
				# TODO : Create registered games list
				r = 'Launching module %s which is a game' % qstr
			
		
			r = bytes(r, 'UTF-8')
		
			self.client.send(r)
		
		# Closing the connection 
		self.client.close()
		del CLIENTS[client_name]
		print ("Client %s is disconnected from the server" % client_name)
		# TODO : Show client IP

def update_registered_mods():
	"""Make a list with all enabled igs mods"""
	
	global REGISTERED_MODS
	
	REGISTERED_MODS = regmods.get()
	
	for mod in REGISTERED_MODS:
		__import__('igsmods.'+mod)
	
	return REGISTERED_MODS


def start_server(HOST, PORT):
	"""Initialize and start IGS"""
	
	global CLIENTS
	
	print ("* START IGS ON %s:%s *" % (HOST, str(PORT)))
	
	# read registered modules
	mods = update_registered_mods()
	print ('Modules list registered on this server :')
	print (mods)
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	try:
		sock.bind((HOST, PORT))
	except socket.error:
		print ("ER: Connection with server fail")
		return 0
	
	print ('Ready...')
	sock.listen(5)
	
	# Waiting for client connection
	# Clients dictionnary
	CLIENTS = {}
	
	while True:
		client, addr = sock.accept()
		
		# New object with that manage the client
		client_thread = Client(client)
		client_thread.start()
		
		# Save connection in the dictionnary
		thread_id = client_thread.getName()
		CLIENTS[thread_id] = client
		
		print ("Client %s is connected (%s:%s)" % (thread_id, addr[0], addr[1]))
		
		#client.send (b"connected")


if __name__ == "__main__":
	# Start IGS
	
	HOST, PORT = igsconfig.get('HOST'), igsconfig.get('PORT')
	
	start_server(HOST,int(PORT))
