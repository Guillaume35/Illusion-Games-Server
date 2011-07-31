import re, path

def get(val):
	"""Return config value"""

	f = open(path.get("config"), 'r')
	
	for line in f:
		if re.search("^"+val+"=", line):
			result = re.sub (val, '', line)
			result = re.sub (r'^.*"(.+)".*\n$', r"\1", result)
			
			f.close()
			
			return result
