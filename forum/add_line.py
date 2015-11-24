from os import walk
import os

mypath="spiders"
files = []
files_to_update=[]
for (dirpath, dirnames, filenames) in walk(mypath):
	files.extend(filenames)
	break

files = set(files)
for foundFile in files:
	splitted= os.path.splitext(foundFile)
	if splitted[-1]==".py" and splitted[0]!="__init__":
		files_to_update.append(foundFile)


print(files_to_update)

for x in files_to_update:
	with open(mypath+"/"+x,'r') as file:
		lines = file.readlines()
		lines[1]=lines[1]+"import dateparser\n"
	with open(mypath+"/"+x,'w') as file:
		for line in lines:
			file.write(line)