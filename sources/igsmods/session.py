import os, hashlib, builtins
import re

def open(user,password):
	"""This function open a new session"""
	
	password = hashlib.md5(bytes(password,'utf-8')).hexdigest()
	
	if os.path.isfile('auth/'+user):
		f = builtins.open ('auth/'+user, 'r')
		p = f.read()
		p = re.sub(r"\s$", "", p)
		
		if p == password:
			r
		
		else:
			r = 'ER: Invalid user/password'
	
	else:
		r = 'ER: Invalid user/password'
		
	return r
