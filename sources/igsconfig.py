import re

def get(val):
	"""Return config value"""
	
	f = open('config', 'r')
	
	for line in f:
		if re.search("^"+val+"=", line):
			result = re.sub (val, '', line)
			result = re.sub (r'^.*"(.+)".*\n$', r"\1", result)
			
			f.close()
			
			return result
