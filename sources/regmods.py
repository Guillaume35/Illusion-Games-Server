import re
import path

def get():
	"""Make a list with all enabled igs mods"""
	
	REGISTERED_MODS = []
	
	f = open(path.get('registered-mods'), 'r')
	
	for line in f:
		mod = re.sub(r'\s*$', '', line)
		mod = re.sub(r'^\s*', '', mod)
		
		if not re.search(r'^#', mod) and re.search(r'^\w+$', mod) and mod not in REGISTERED_MODS:
			REGISTERED_MODS.append(mod)
	
	f.close()
	
	return REGISTERED_MODS
