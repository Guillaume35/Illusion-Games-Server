#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import os, hashlib
import igsconfig, socket, re

def new_su():
	"""Create a new super user"""
	
	print ('Enter "cancel" to exit all')
	
	while 1:
		u = input ('Enter a username : ')
		
		if u == "cancel" or u == "c":
			print ('Cancel operation.')
			return 0
		
		syntax = 0
		if re.search(r'^[\w\-]+[\w\-\.@]*\w+$', u):
			syntax = 1
			
			if os.path.isfile('auth/'+u):
				print ("ER: This username is already registered. Choose one other.")

			else:
				break
		
		if not syntax:
			print ("ER: Username should contain only chars like a-z,A-Z,0-9,_-@")
	
	while 1:
		p = input ('Enter a password : ')
		
		if p == "cancel" or p == "c":
			print ('Cancel operation.')
			return 0
		
		if len(p) < 6:
			print ('ER: Password must have more than 6 chars')
		else:
			break
		
	p = hashlib.md5(bytes(p,'utf-8')).hexdigest()
	
	try:
		f = open ('auth/'+u, 'w')
		f.write(p)
		f.close()
		
		print (u+' has been created !')
	except:
		print ("ER: I/O error, unable to save this user")


def remove_su():
	"""Remove a super user from auth"""
	
	print ('Enter "cancel" to exit all')
	
	while 1:
		u = input ('Enter the username you want to remove : ')
		
		if u == "cancel" or u == "c":
			print ('Cancel operation.')
			return 0
		
		if os.path.isfile('auth/'+u):
			break
		
		print ('ER: This username does not exist')
	
	while 1:
		r = input ('Are you sure you want to remove '+u+' ? (yes/no) ')
		
		if r == 'yes' or r == 'y' or r == '1':
			try:
				os.remove('auth/'+u)
				print (u+" has been removed")
				break
			except:
				print ('ER: I/O error, unable to delete the file')
				break
		else:
			print ('Cancel operation.')
			return 0
	return 0
		

def main():
	"""The main function"""	
	
	# Connection to IGS
	try:
		sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except:
		print ("ER: Unable to connect the server")
		return 0
	
	try:
		sock.connect(('localhost', int(igsconfig.get('PORT'))))
	except:
		print ("ER: Unable to connect the server");
		return 0
		
	print ('What do you want to do ?')
	print ("\t1. Create a new super user")
	print ("\t2. Remove a super user")
	print ("\texit")
	
	# Selecting choice
	while 1:	
		r = input ('> ')
		
		if r == '1' or r == '2' or r == 'exit' or r == 'quit':
			break
		else:
			print ('ER: Wrong choice')
	
	if r == '1':
		new_su()
	
	elif r == '2':
		remove_su()
	
	elif r == 'exit' or r == 'quit':
		sock.close()
		return 0
	
	else:
		print ("ER: Wrong choice")
	
	sock.close()
	return 0


if __name__ == "__main__":
	main()
	
