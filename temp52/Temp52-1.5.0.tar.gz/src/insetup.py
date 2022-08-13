#In the name of GOD
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import sqlite3
import update

main_direct = ['AI', 'Config', 'Database', 'DCC1', 'GUI', 'GUI\\Temp', 'GUI\\API', 'GUI\\AuiPanel', 'GUI\\Main',
               #'Locale', 'Locale\\en', 'Locale\\fa', 'Locale\\fr', 'Locale\\gr', 'Locale\\sp', 'Locale\\tr',
               'Logs', 'Res', 'Res\\Fonts', 'Res\\Icons', 'Res\\Icons\\Menu', 'Res\\Icons\\Toolbar',
               'Res\\Icons\\16x16', 'Res\\Icons\\32x32', 'Res\\Images', 'Res\\Pics', 'Res\\Splash',
               'Src', 'Src\\API', 'Src\\AUI', 'Src\\DBF', 'Src\\DBF\\sqls', 'Src\\GUI', 'Src\\MLA', 'Src\\MLP', 'Src\\PRG',
               'Temps', 'Utility', 'Utility\\Fount', 'Utility\\Fount\\GUI', 'Utility\\Fount\\MLA', 'Utility\\Fount\\MLP',
               'Utility\\Fount\\AUI', 'Utility\\Fount\\PRG', 'Utility\\Fount\\API', 'Utility\\UpdateApp',
               'Utility\\Account','Utility\\Uploads','Utility\\Downloads'
               ]

local_direct = ['Locale', 'Locale\\en', 'Locale\\fa', 'Locale\\fr', 'Locale\\gr', 'Locale\\sp', 'Locale\\tr']

main_file = {
	'AI': ['OpnSrc.py', 'Generats.py', 'DBgen.py', 'Analiz.py'],
    'Config': ['Init.py'],
    'Database': ['wxsq.py', 'PostGet2.py', 'PostGet.py', 'MenuSet2.py','srcsql.py','dbinterface.py'],
	'DCC1': ['Proper2.py', 'MenuDev2.py', 'DBDev2.py', 'ToolBar2.py', 'ProgDev2.py', 'MLDev2.py', 'ListPro2.py', 'AuiPan2.py'],
	'GUI': ['window2.py', 'Start.py', 'proman.py', 'MainTool.py', 'MainMenu2.py', 'BG2.py'],
	'GUI\\Temp': ['untitle.py', 'Demo.py', 'Muntitle.py'],
	'GUI\\API': ['SamPnl.py'],
	'GUI\\AuiPanel': ['tempane.py', 'PAui.py'],
	'GUI\\Main': ['TPv1.py', 'TBv1.py', 'PPv1.py', 'PGv1.py', 'PAv1.py', 'MLv1.py', 'MDv1.py', 'DBv1.py'],
	'Res': ['Allicons.py'],
}

creat_file = {
	'Config': ['MLmethod.ini', 'option.ini', 'system1.ini'],
	'Database': ['Menu2.db'],
	#'Locale':[''],{'en':'','fa':'','fr':,'','gr':'','sp':'','tr':''},
	'..': ['Mainpro.py','update.py','requirements.txt','Allimp.py']
}

def create_this(file,source,target):
	if file == 'Menu2.db':
		print('.',end='')
		connection = sqlite3.connect(target+file)
		cursor = connection.cursor()
		with open(source+'Createmenu.sql', 'r') as f:
			cursor.executescript(f.read())
		connection.commit()
		connection.close()
	else:
		print('.', end='')
		shutil.copyfile(source + file, target + file)


def main(argv):
	mydir = input("Please write directory to like install program:[sample: c:\Temp5\] >> ")

	if mydir == '':
		print('Exit setup. you not entered anything')
		exit()
	if mydir[-1] != '\\':
		print('Write a correct directory format')
		exit()

	if not os.path.isdir(mydir):
		print('.', end='')
		os.mkdir(mydir)

	os.chdir(mydir)

	for dir in main_direct:
		if not os.path.isdir(dir):
			os.mkdir(dir)
			print('.', end='')
			if not os.path.isfile(mydir+dir+'\\'+'__init__.py'):
				with open(mydir +dir+'\\'+'__init__.py','w') as f:
					f.write('')
					print('.', end='')

	for dir in local_direct:
		if not os.path.isdir(dir):
			os.mkdir(dir)
			print('.', end='')

	for dir in main_file:
		for fil in main_file[dir]:
			if not os.path.isfile(mydir+dir+'\\'+fil):
				with open(mydir+dir+'\\'+fil,'w') as f:
					f.write('')
					print('.', end='')

	for Dir in creat_file:
	   for file in creat_file[Dir]:
		   if Dir != '..':
			   if not os.path.isfile(mydir+Dir+'\\'+file):
				   with open(mydir+Dir+'\\'+file,'w') as f:
					   f.write('')
					   print('.', end='')
		   else:
			   with open(mydir+ file, 'w') as f:
				   f.write('')
				   print('.', end='')

	for Dir in creat_file:
		for file in creat_file[Dir]:
			if Dir != '..':
				if os.stat(mydir+Dir+'\\'+file).st_size == 0:
					create_this(file,'c:\\MPT5\\Fount\\',mydir+Dir+'\\')
			else:
				if os.stat(mydir+file).st_size == 0:
					create_this(file,'c:\\MPT5\\Fount\\',mydir)

	update.main()


if __name__ == '__main__':
	main(sys.argv)