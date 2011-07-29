import pickle, hashlib

def new(user, password):
	"""Add a user and password in users file"""
	
	if user == '' or password == '':
		return 0
	
	with open('../auth/users', 'rb') as f:
		fp = pickle.Unpickler(f)
		ls_users = fp.load()
	
	if not user in ls_users:
		with open ('../auth/users', 'wb') as f:
			md5pwd	= hashlib.md5(bytes(password,'utf-8')).hexdigest()
			
			ls_users[user] = md5pwd
			
			fp = pickle.Pickler(f)
			fp.dump(ls_users)
			
			return 1
	
	return 0
