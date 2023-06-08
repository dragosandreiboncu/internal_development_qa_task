import sys
import os
from os import path
from datetime import datetime, timedelta
import time
from hashlib import md5
from shutil import copyfile

def args_verification(argv):
	if len(sys.argv) != 5:
		print("Incorect number of arguments.\nYou need to add source path, replica path, sync interval in seconds and log file path.")
		sys.exit()
	if path.exists(sys.argv[1]) is False:
		print("Source path doesn't exist.")
		sys.exit()
	if path.exists(sys.argv[2]) is False:
		print("Replica path doesn't exist.")
		sys.exit()
	if sys.argv[3].isnumeric() is False:
		print("Synchronization interval is not a number.")
		sys.exit()
	global logFile
	if path.exists(sys.argv[4]) is False:
		print("Log file doesn't exist.")
		try:
			logFile = open(sys.argv[4], "x")
		except:
  			print("Cannot create the log file")
  			sys.exit()
		else:
			print("A log file was created.")
  		
  		
def log_write(msg):
	time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	log = time + " - " + msg
	print(log)
	try:
		logFile.write(log)
		logFile.write("\n")
	except:
  		print("Cannot write in log file")
  		
def check_files(sourcePath, replicaPath, filename1, filename2):
	try:
		s_open = open(sourcePath + "/" + filename1,"rb")
		r_open = open(replicaPath + "/" + filename2,"rb")
		s_bytes = s_open.read()
		r_bytes = r_open.read()
	except:
		print("Cannot check files")
		sys.exit()
	else:
		s_hash = md5(s_bytes).hexdigest()
		r_hash = md5(r_bytes).hexdigest()
		if s_hash == r_hash:
			return True
	return False


def sync_folders(sourcePath, replicaPath):
	sourceFiles = os.listdir(sourcePath)
	replicaFiles = os.listdir(replicaPath)
	syncFiles = []
	# checking what files we already have similar
	for sourceFile in sourceFiles:
		if sourceFile in replicaFiles:
			if check_files(sourcePath, replicaPath, sourceFile, sourceFile):
				syncFiles.append(sourceFile)
	# checking if we have similar files but renamed
	for replicaFile in replicaFiles:
		if replicaFile not in syncFiles:
			fileRenamed = False
			for sourceFile in sourceFiles:
				if sourceFile not in syncFiles:
					sourceFileSize = os.stat(sourcePath + "/" + sourceFile).st_size
					replicaFileSize = os.stat(replicaPath + "/" + replicaFile).st_size
					if sourceFileSize == replicaFileSize:
						# if their size is equal then files might be similar
						if check_files(sourcePath, replicaPath, sourceFile, replicaFile):
							syncFiles.append(sourceFile)
							os.rename(replicaPath + "/" + replicaFile, replicaPath + "/" + sourceFile)
							log_write("File " + replicaFile + " has been renamed to " + sourceFile)
							fileRenamed = True
							break
			# if only their size is similar or not even that then we should delete that replica file
			if fileRenamed is False:
				log_write("File " + replicaFile + " has been removed")
				os.remove(replicaPath + "/" + replicaFile)
	# finally every file that is not present in replica folder should be copied
	for sourceFile in sourceFiles:
		if sourceFile not in syncFiles:
			try:
				s_open = open(sourcePath + "/" + sourceFile,"r")
				r_open = open(replicaPath + "/" + sourceFile,"x")
				log_write("File " + sourceFile + " has been created")
				r_open = open(replicaPath + "/" + sourceFile,"w")
				copyfile(sourcePath + "/" + sourceFile, replicaPath + "/" + sourceFile)
				log_write("File " + sourceFile + " has been fully copied")
			except:
				print("Cannot copy files")
				sys.exit()




sourcePath = sys.argv[1]
replicaPath = sys.argv[2]
syncInterval = sys.argv[3]
logFilePath = sys.argv[4]

while True:
	print("Synchronization in progress...")
	args_verification(sys.argv)
	try:
		logFile = open(sys.argv[4], "a")
	except:
  		print("Cannot open the log file") 
  		sys.exit()
	sync_folders(sourcePath, replicaPath)
	logFile.close()
	interval = datetime.now() + timedelta(seconds=int(syncInterval))
	print("Successfully synchronized.\n\n")
	while datetime.now() < interval:
		time.sleep(1)



