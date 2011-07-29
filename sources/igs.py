import socket, threading, igsconfig, re

# initializing
registered_mods = []
clients = 0

def update_registered_mods():
	"""Make a list with all enabled igs mods"""
	
	global registered_mods
	registered_mods = [] # re-initializing registered_mods
	
	f = open('registered-mods', 'r')
	
	for line in f:
		mod = re.sub(r'\s*$', '', line)
		mod = re.sub(r'^\s*', '', mod)
		
		if not re.search(r'^#', mod) and re.search(r'^\w+$', mod) and mod not in registered_mods:
			registered_mods.append(mod)
	
	f.close()
	
	return registered_mods
			

def main_loop(sock):
	"""Accept connections and for each, call handler() in a new thread"""

	while True:
		client, addr = sock.accept()
		print ("Client %s is connecting"%addr[0])
		
		# Start a new thread for this client
		threading.Thread(target=handler, args=(client,  addr)).start()


def handler(client, addr):
	"""Execute client query"""
	
	global clients
	clients += 1
	
	# Test security filter TODO
	security = igsconfig.get('SECURITY')
	access = 1

	while True:
		q = client.recv(1024)
		
		if not q: #If disconnected
			break
		
		qstr = str(q)
		qstr = re.sub(r"^b'", "", qstr)
		qstr = re.sub(r"'$", "", qstr)
		qstr = re.sub(r'^b"', '', qstr)
		qstr = re.sub(r'"$', '', qstr)
		
		if re.search(r"^igs\.", qstr):
			qstr = re.sub(r"^igs\.", r"igsmods.", qstr)
			
			mod = re.sub(r"^igsmods\.(\w+)\.\w+\(.*\)\s*", r"\1", qstr)
			
			if mod in registered_mods:
				#try:
				exec ("import igsmods."+mod)
				r = eval(qstr)
				#except:
				#	r = 'ER: There where a problem in your command execution. Check the syntax'
			
			else:
				r = 'ER: Module '+mod+' could not be found in IGS registered modules list'
		
		else:
			r = 'Launching module '+qstr+' which is a game'
		
		r = bytes(r, 'UTF-8')
		
		client.send(r)
	
	print ("Client %s is disconnected from the server"%addr[0])


def start_server(HOST, PORT):
	"""Initialize and start IGS"""
	
	# read registered modules
	mods = update_registered_mods()
	print ('Modules list registered on this server :')
	print (mods)
	
	sock = socket.socket()
	sock.bind((HOST, PORT))
	sock.listen(5)
	main_loop(sock)


if __name__ == "__main__":
	# Start IGS
	
	HOST, PORT = igsconfig.get('HOST'), igsconfig.get('PORT')
	
	print ("* START IGS ON "+HOST+":"+PORT+" *")
	
	start_server(HOST,int(PORT))
