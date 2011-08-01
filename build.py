import os
import re, shutil

def getconfig(val):
	"""Return config value"""
	
	try:
		f = open('build.conf', 'r')
	except:
		print ('ER: I/O error, unable to read build.conf')
		return 0
	
	for line in f:
		if re.search("^"+val+"=", line):
			result = re.sub (val, '', line)
			result = re.sub (r'^.*"(.*)".*\n$', r"\1", result)
			
			f.close()
			
			return result

def mk_dir(DIR):
	"""Create working directory"""
	
	if os.path.exists(DIR):
		if os.path.isdir(DIR):
			try:
				shutil.rmtree(DIR)
			except:
				print ("ER: I/O error, unable to remove %s/" % DIR)
				return 0
		else:
			r = input ('%s seams to be a file. Building IGS will remove it. Do you want to continue ? (y/n)')
			
			yesans = ('yes','y','1','true','ok')
			if r in yesans:
				try:
					os.remove(DIR)
				except:
					print ("ER: I/O error, unable to remove %s" % DIR)
					return 0
			else:
				print ('Cancel operation.')
				return 0
	
	try:
		os.makedirs(DIR)
		print ('Make %s directory' % DIR)
		return 1
	except:
		print ('ER: I/O error, unable to create %s/' % DIR)
	
	return 0

def create_structure(DIR, STRUCTURE, REPATH):
	"""Create the path structure in DIR"""
	
	try:
		f = open('sources/paths/'+STRUCTURE, 'r')
	except:
		print ('ER: I/O error, unable to read sources/paths/%s' % STRUCTURE)
		return 0
	
	root_path = DIR+'/struct'
	created = []
	copied_files = {}
	r = ''
	r1 = ''
	
	for line in f:
		if re.search(r"^[\w/\.]+\s*=", line):
			path = re.sub (r'^([\w/\.]+)\s*=.*\n$', r"\1", line)
			
			if path != '' and not re.search(r'^\s*$', path):
				try:
					if path not in created:
						# Create dir in structure
						os.makedirs(root_path+path)
						print (root_path+path+" created!")
					
					# Add files in dir
					files = re.sub(r'^[\w/\.]+\s*=\s*(.*)\n$', r'\1', line)
					files = re.sub(r'^\s*', '', files)
					files = re.sub(r'\s*$', '', files) #TODO : maybe one exp only
					
					files_ls = files.split(' ')
					
					for fl in files_ls:
						if re.search(r'>', fl):
							fl_rname = fl.split('>')
							fl = fl_rname[0]
							fl_new = fl_rname[1]
						else:
							fl_new = fl
						
						if os.path.exists('sources/'+fl) and fl not in copied_files.keys():
							if os.path.isdir('sources/'+fl):
								try:
									shutil.copytree('sources/'+fl, root_path+path+fl_new)
									print ('Copy directory sources/%s > %s/%s' % (fl, root_path, path))
									copied_files[fl] = root_path+path+fl_new
								except:
									print ('ER: Unable to copy dir sources/%s > %s/%s' % (fl,root_path,path))
									if not r1 == 'yes for all':
										r1 = input ('This directory have not been copied. Your IGS build might be broken or unstable. Do you want to continue ? (yes,yes for all, no) ')
										yes_ans = ('yes','y','1','yes for all','true')
										if r1 not in yes_ans:
											print ('Cancel operation.')
											f.close()
											return 0
							else:
								try:
									just_fl = re.sub(r'^.*/([\w\.-]+)$', r'\1', fl_new)
									shutil.copy('sources/'+fl, root_path+path+just_fl)
									print ('Copy file sources/%s > %s/%s' % (fl, root_path, path))
									copied_files[fl] = root_path+path+just_fl
								except:
									print ('ER: Unable to copy file sources/%s > %s/%s' % (fl,root_path,path))
									if not r1 == 'yes for all':
										r1 = input ('This file have not been copied. Your IGS build might be broken or unstable. Do you want to continue ? (yes,yes for all, no) ')
										yes_ans = ('yes','y','1','yes for all','true')
										if r1 not in yes_ans:
											print ('Cancel operation.')
											f.close()
											return 0
								
						else:
							print ('File sources/%s do not exits. Ignore it.' % fl)
					
					created.append(path)
				except:
					print ("ER: I/O error, unable to create "+root_path+path)
					if not r == 'yes for all':
						r = input ('This directory have not been created in the structure. Your IGS build might be broken or unstable. Do you want to continue ? (yes,yes for all, no) ')
						
						yes_ans = ('yes','y','1','yes for all','true')
						if r not in yes_ans:
							print ('Cancel operation.')
							f.close()
							return 0
	
	f.close()
	
	# Replace file structure in .py files
	if REPATH:
		print ('Starting Re-path')
		for fl in copied_files:
			if re.search(r'\.py$', copied_files[fl]):
				try:
					f = open (copied_files[fl], 'r')
					next = True
				except:
					print ('ER: I/O error, Unable to open %s.' % copied_files[fl])
					next = False
			
				if next:
					fl_content = ''
					
					for line in f:
						while re.search('^.*path\\.get\\(["\'].+?["\']\\).*\\n$', line):
							fl_base = re.sub (r'^.*path\.get\((.+?)\).*\n$', r'\1', line)
							fl_key = re.sub ('^[\\s"\']*', r'', fl_base)
							fl_key = re.sub ('[\\s"\']*$', r'', fl_key)
						
							if fl_key in copied_files:
								real_file = re.sub(r'^'+DIR+'/struct', r'', copied_files[fl_key])
								line = re.sub(r'path\.get\('+fl_base+'\)', r'"'+real_file+'"', line)
								print ('Found ' + fl_key + ' which is in '+real_file)
							else:
								line = re.sub(r'path\.get\('+fl_base+'\)', r'"'+fl_key+'"', line)
								print ('Found %s and set it to default value' % fl_key)
						
						fl_content += line
					f.close()
			
					try:
						f = open (copied_files[fl], 'w')
						next = True
					except:
						print ('ER: I/O error, unable to open %s for writing.' % copied_files[fl])
						next = False
				
					if next:
						try:
							f.write(fl_content)
							print ('%s is re-pathed!' % copied_files[fl])
						except:
							print('ER: I/O error, unable to write in %s.' % copied_files[fl])
						f.close()
	
	return 1

def mk_deb(DIR):
	"""Create the .deb file"""
	
	print ('Start debian package creation')
	
	deb_dir = DIR+'/debian'
	try:
		shutil.copytree(DIR+'/struct', deb_dir)
		print ('Structure copied to %s' % deb_dir)
	except:
		print ('ER: I/O error, unable to create %s and copy files' % deb_dir)
		return 0
	
	try:
		os.makedirs(deb_dir+"/DEBIAN")
		print ('%s/DEBIAN created' % deb_dir)
	except:
		print ('ER: I/O error, unable to create %s/DEBIAN' % deb_dir)
		return 0
	
	try:
		shutil.copy('build-tools/debian/control', deb_dir+'/DEBIAN')
		shutil.copy('build-tools/debian/perm', deb_dir+'/DEBIAN')
		shutil.copy('build-tools/debian/postinst', deb_dir+'/DEBIAN')
	except:
		print ('ER: I/O error, unable to copy build-tools/debian/control')
		return 0
	
	try:
		os.system('build-tools/debian/create_md5 '+os.environ['PWD']+'/'+deb_dir)
	except:
		print ('ER: Unable to execute build-tools/debian/create_md5')
		return 0
	
	try:
		os.system('build-tools/debian/make-deb '+os.environ['PWD']+'/'+DIR)
	except:
		print ('ER: Unable to execute build-tools/debian/make-deb')
		return 0
		
	return 1

def mk_archive(DIR):
	"""Create .tar.gz archive"""
	
	tar_dir = DIR+'/igs'
	
	try:
		shutil.copytree(DIR+'/struct', tar_dir)
		print ('Structure copied to %s' % tar_dir)
	except:
		print ('ER: I/O error, unable to create %s and copy files' % deb_dir)
		return 0
	
	try:
		os.system('build-tools/create_tar '+os.environ['PWD']+'/'+DIR)
	except:
		print ('ER: Unable to execute build-tools/create_tar')
		return 0
	
	return 1

def install(DIR,PACKAGE):
	"""Install package on the computer"""
	
	if not PACKAGE.upper() == 'DEB':
		print ('Package installation is only available for *.deb file.')
		r = input ('Do you want to continue the process ? (yes/no)')
		
		ans_ls = ['YES','Y','1']
		if r.upper() in ans_ls:
			return 1
		else:
			return 0
	
	try:
		os.system('build-tools/debian/install '+os.environ['PWD']+'/'+DIR)
	except:
		print ('ER: Unable to execute build-tools')
	
	return 1
	

def main():
	"""Main function of the program"""
	
	# Initializing values :
	DIR = getconfig('dir')
	AFTER = getconfig('after')
	STRUCTURE = getconfig('structure')
	PACKAGE = getconfig('package')
	REPATH = getconfig('repath')
	
	if REPATH.upper() == 'TRUE' or REPATH == '1': REPATH = True
	else: REPATH = False
	
	dir_v, after_v, structure_v, package_v, repath_v = DIR, AFTER, STRUCTURE, PACKAGE, REPATH
	
	if not dir_v: dir_v = '(empty value)'
	if not after_v: after_v = '(empty value)'
	if not structure_v: structure_v = '(empty value)'
	if not package_v: package_v = '(empty value)'
	if not repath_v: repath_v = '(empty value)'
	
	# Return values
	print ('Default configuration :')
	print ('\tDIR          = %s/' % dir_v)
	print ('\tAFTER        = %s' % after_v)
	print ('\tSTRUCTURE    = %s' % structure_v)
	print ('\tPACKAGE      = %s' % package_v)
	print ('\tREPATH       = %s' % repath_v)
	
	say_er = 'Unable to finish build'
	
	if not mk_dir(DIR):
		print (say_er)
		return 0
	if not create_structure(DIR,STRUCTURE,REPATH):
		print (say_er)
		return 0
	if PACKAGE.upper() == 'DEB':
		if not mk_deb(DIR):
			print (say_er)
			return 0
	elif PACKAGE.upper() == 'ARCHIVE':
		if not mk_archive(DIR):
			print (say_er)
			return 0
	else:
		print ('No valid package type selected.')
	
	if re.search(r'INSTALL', AFTER.upper()):
		if not install(DIR,PACKAGE):
			print (say_er)
			return 0
	
	if re.search(r'DELETE', AFTER.upper()):
		try:
			shutil.rmtree(DIR)
			print ('Delete %s/ after the process.' % DIR)
		except:
			print ('Unable to delete %s/' % DIR)
	
	print ('END.')
	return 0

if __name__ == "__main__":
	main()
